from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from backend.models import User,EncryptFile
from config.config import SUCCESS,ERROR
from .pb_fun import judge_user

# 日志对象
from config.logger import logger_backend

# Create your views here.

def login(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  if user.dataowner == True:
    response = JsonResponse({
      "status":SUCCESS,
      "dataowner":True
    })
  else:
    response = JsonResponse({
      "status":SUCCESS,
      "dataowner":False
    })
  # username = request.POST["username"]
  # password = request.POST["password"]
  # autoLogin = request.POST["autoLogin"]
  # if autoLogin == "true":
  #   max_age = 30*24*60*60
  #   response.set_cookie("searchable_encryption_username",username,max_age=max_age)
  #   response.set_cookie("searchable_encryption_password",password,max_age=max_age)
  # else:
  #   response.set_cookie("searchable_encryption_username",username)
  #   response.set_cookie("searchable_encryption_password",password)
  
  logger_backend.debug("用户:{} 登录 dataowner={}".format(user.username,user.dataowner))
  return response


def register(request):
  if request.method != "POST":
    return JsonResponse({
      "status":ERROR,
      "information":"请求方式错误"
    })
  username = request.POST["username"]
  password = request.POST["password"]
  try:
    User.objects.get(username=username)
  except User.DoesNotExist:
    user = User(username=username,password=password)
    user.save()
  else:
    return JsonResponse({"status":ERROR,"information":"用户名重复"})
  
  # debug时偷看一下
  logger_backend.debug("用户:{} 注册 password={}".format(username,password))
  return JsonResponse({"status":SUCCESS})

def login_confirm(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response
  response = {
    "status":SUCCESS
  }
  if user.dataowner == True:
    response["dataowner"] = True
  else:
    response["dataowner"] = False
  if EncryptFile.objects.count() > 0:
    response["builded"] = True
  else:
    response["builded"] = False
  return JsonResponse(response)

def logout(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)

  response = JsonResponse({
    "status":SUCCESS
  })

  response.set_cookie("searchable_encryption_username","",max_age=-1)
  response.set_cookie("searchable_encryption_password","",max_age=-1)

  return response