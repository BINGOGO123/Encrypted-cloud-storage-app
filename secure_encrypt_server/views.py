from django.shortcuts import render
from django.http import JsonResponse
import chardet
import os
import json
import ipdb
import base64
import re

from django.conf import settings
from .models import SecureFile,Label
from backend.models import EncryptFile,UserAttribute
from backend.models import User
from config.config import SUCCESS,ERROR
from backend.views.pb_fun import judge_user
from .tf_idf import tf_idf
from .essential import getInMemoryUploadedFile_bytes
from .encrypt import getPassword,encrypt_aes,decrypt_aes,pad,get_md5_value

# 日志对象
from config.logger import logger_server
# Create your views here.

def remove_file(filename):
  if os.path.exists(filename):
    try:
      os.remove(filename)
    except:
      logger_server.exception("remove_file {filename} 删除失败".format(filename))

def upload(request):
  # ipdb.set_trace()
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您无权限上传文件"
    })

  # 检查是否是同一批次，如果不是则删掉之前上传的文件，但是这里的删除只是删除数据库表而不是删除文件
  label_id = request.POST["label"]
  if Label.objects.count() <= 0:
    Label.objects.create(label=label_id)
  else:
    label = Label.objects.all()[0]
    if label.label != label_id:
      # 首先删除所有的本地文件
      secure_files = SecureFile.objects.all()
      for secure_file in secure_files:
        filename = settings.MEDIA_ROOT + secure_file.secure_file.name
        remove_file(filename)
      secure_files.delete()
    label.label = label_id
    label.save()

  # urls = []
  # ids = []
  # status = SUCCESS
  # information = ""
  # for one_file in request.FILES:
  #   if request.FILES[one_file].size <= 0:
  #     status = ERROR
  #     information = "无法加载空文件"
  #     urls.append("")
  #     ids.append("")
  #   else:
  #     secure_file = SecureFile(secure_file=request.FILES[one_file])
  #     secure_file.save()
  #     urls.append(request.build_absolute_uri(settings.MEDIA_URL + secure_file.secure_file.name))
  #     ids.append(secure_file.id)

  one_file = request.FILES['file']
  if one_file.size <= 0:
    return JsonResponse({
      "status":ERROR,
      "information":"无法加载空文件"
    })

  current_secure_files = SecureFile.objects.all()
  data = one_file.read()
  md5 = get_md5_value(data)
  for secure_file in current_secure_files:
    if secure_file.md5 == md5:
      return JsonResponse({
        "status":ERROR,
        "information":"不加载重复文件"
      })
  secure_file = SecureFile(secure_file = one_file,md5=md5)
  secure_file.save()
  url = request.build_absolute_uri(settings.MEDIA_URL + secure_file.secure_file.name)
  file_id = secure_file.id

  return JsonResponse({
    "status":SUCCESS,
    "url":url,
    "id":file_id
  })

def upload_ex(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您无权限设定权限表达式"
    })

  file_id = request.POST["file_id"]
  ex = request.POST["ex"]

  try:
    secure_file = SecureFile.objects.get(id=file_id)
    secure_file.ex = ex
    secure_file.save()
  except SecureFile.objects.DoesNotExist:
    logger_server.error("upload_ex 文件不存在 file_id={}".format(file_id))
    return JsonResponse({
      "status":ERROR,
      "information":"该文件不存在"
    })
  
  return JsonResponse({
    "status":SUCCESS
  })

def giveup_upload(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您无操作权限"
    })
  
  secure_files = SecureFile.objects.all()
  for secure_file in secure_files:
    filename = settings.MEDIA_ROOT + secure_file.secure_file.name
    remove_file(filename)
  secure_files.delete()
  Label.objects.all().delete()

  return JsonResponse({
    "status":SUCCESS
  })

def build_searchable_cloud_syetem(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您无操作权限"
    })
  
  if Label.objects.count() <= 0:
    logger_server.error("build_searchable_cloud_syetem label不存在")
    return JsonResponse({
      "status":ERROR,
      "information":"没有标记"
    })
  
  label = Label.objects.all()[0]
  if label.label != request.POST["label"]:
    logger_server.error("build_searchable_cloud_syetem label不吻合 server_label={} client_label={}".format(label.label,request.POST["label"]))
    return JsonResponse({
      "status":ERROR,
      "information":"标记不吻合"
    })

  # 对所有文件运行tf-idf算法，生成关键词分数向量
  secure_files = SecureFile.objects.all()
  original_data = []
  original_filename = []
  data_lib = []
  for secure_file in secure_files:
    filename = secure_file.secure_file.name
    original_filename.append("".join(filename.split("/")[1:]))
    f = open(settings.MEDIA_ROOT + filename,"rb")
    data = f.read()
    f.close()
    # 将填充后的二进制加入到原始数据列表中
    original_data.append(pad(data))
    encoding = chardet.detect(data)["encoding"]
    data = data.decode(encoding)
    # 这里需要全部变成小写，防止搜索时大小写不匹配的问题
    data_lib.append(data.lower())

  # 关键词表，加密分数向量表，加密矩阵，解密矩阵
  word,encrypt_score,encrypt_matrix,decrypt_matrix = tf_idf(data_lib)

  # 生成128位aes密钥
  aes_password = getPassword(16)

  # 删除EncryptFile中目前的文件
  if EncryptFile.objects.count() > 0:
    encrypt_files = EncryptFile.objects.all()
    for encrypt_file in encrypt_files:
      filename = settings.MEDIA_ROOT + encrypt_file.encrypt_file.name
      remove_file(filename)
    encrypt_files.delete()

  # 分别对原文数据加密并保存
  for i in range(len(original_data)):
    data = original_data[i]
    filename = original_filename[i]

    c_data = encrypt_aes(data,aes_password)
    pic_file = getInMemoryUploadedFile_bytes(c_data,filename)

    ex = secure_files[i].ex
    encrypt_file = EncryptFile(encrypt_file=pic_file,permission=ex,encrypt_vector=json.dumps(encrypt_score[i]))
    encrypt_file.save()

  # 删除所有的secure_file和label
  for secure_file in secure_files:
    filename = settings.MEDIA_ROOT + secure_file.secure_file.name
    remove_file(filename)
  secure_files.delete()
  Label.objects.all().delete()

  # 大功告成准备返回数据，因为不支持传输bytes类型，所以先转换成list
  aes_password_list = [x for x in aes_password]
  response = {
    "status":SUCCESS,
    "secret":{
      "aes_secret":aes_password_list,
      "word":word,
      # "encrypt_matrix":encrypt_matrix,
      "decrypt_matrix":decrypt_matrix
    }
  }

  # debug时查看一下返回的信息
  logger_server.debug("build_searchable_cloud_syetem response={}".format(response))

  return JsonResponse(response)

# 向量相乘
def vector_dot(vector1,vector2):
  if len(vector1) != len(vector2):
    return "len_err"
  return sum([vector1[x] * vector2[x] for x in range(len(vector1))])

# 解密文件
def decrypt_file(filename,password):
  f = open(filename,"rb")
  c_data = f.read()
  f.close()
  # print(password)
  data = decrypt_aes(c_data,password)
  encoding = chardet.detect(data)["encoding"]
  # 如果解密之后找不到编码的格式，那么说明密钥错误
  if encoding == None:
    return False,False
  # print(encoding)
  return data.decode(encoding),c_data

# 将ex中的属性替换成0或1
def to_logic_ex(ex,attributes):
  # 去掉所有空白符
  regular = re.compile(r"""\s""")
  ex = regular.sub("",ex)
  # 前后都加一个空格
  ex = " " + ex + " "
  # 将拥有的属性替换为1，被替换的属性前后必须是&|!()或者空格才行
  for attribute in attributes:
    regular = re.compile(r"""(?<=[\s&|!()])""" + attribute + r"""(?=[\s&|!()])""")
    ex = regular.sub("1",ex)
  # 去掉表达式前后的空格
  ex = ex.replace(" ","")
  
  # 将非&|!()1的字符串替换成0
  regular = re.compile(r"""[^1&|!()]+""")
  ex = regular.sub("0",ex)

  # 将&|!分别变成 and or not
  ex = ex.replace("&"," and ")
  ex = ex.replace("|"," or ")
  ex = ex.replace("!"," not ")
  return ex

# 计算表达式ex的值，递归函数
def compute_ex(ex):
  # 如果没有表达式则返回True
  if ex == "":
    return 1
  try:
    value = eval(ex)
    return value
  except SyntaxError:
    return "error"

def search_file(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  attributes = UserAttribute.objects.filter(user=user)
  attributes = [attribute.attribute for attribute in attributes]

  aes_secret = bytes([int(x) for x in request.POST["aes_secret"].split(",")])
  tw = [float(x) for x in request.POST["tw"].split(",")]
  encrypt_files = EncryptFile.objects.all()
  score_list = []
  for encrypt_file in encrypt_files:
    if user.dataowner != True:
      ex = encrypt_file.permission
      if ex != None:
        ex = to_logic_ex(ex,attributes)
        value = compute_ex(ex)
        if value == "error":
          logger_server.error("search_file ex不合法 filename={} permission={} attributes={} ex={} user={}".format(encrypt_file.filename,encrypt_file.permission,attributes,ex,user.username))
        # 没有访问权限
        elif value == 0:
          logger_server.debug("search_file 没有访问权限 user={} attributes={} permission={}".format(user.username,attributes,encrypt_file.permission))
          continue
    score = vector_dot(tw,json.loads(encrypt_file.encrypt_vector))
    if score == "len_err":
      logger_server.debug("search_file 陷门向量长度不对 encrypt_vector={} tw={}".format(json.loads(encrypt_file.encrypt_vector),tw))
      return JsonResponse({
        "status":ERROR,
        "information":"密钥错误"
      })
    # 只保留5位小数，因为有很多约等于0的数字
    score_list.append([round(score,5),encrypt_file])

  # 按照从大到小排序
  score_list.sort(key=lambda x:x[0],reverse=True)
  # 只要score大于0的
  file_list = []
  for score_file in score_list:
    score,encrypt_file = score_file
    if score > 0:
      text,c_data = decrypt_file(settings.MEDIA_ROOT + encrypt_file.encrypt_file.name,aes_secret)
      if text==False and c_data == False:
        logger_server.debug("search_file 解密密钥错误 aes_secret={}".format([x for x in aes_secret]))
        return JsonResponse({
          "status":ERROR,
          "information":"密钥错误"
        })
      file_list.append({
        "name":"".join(encrypt_file.encrypt_file.name.split("/")[1:]),
        "text":text,
        "encrypt_text":base64.b64encode(c_data).decode("ascii"),
        "download_url":request.build_absolute_uri(settings.MEDIA_URL + encrypt_file.encrypt_file.name),
        "display":0
      })
    else:
      break
  
  return JsonResponse({
    "status":SUCCESS,
    "file_list":file_list
  })
