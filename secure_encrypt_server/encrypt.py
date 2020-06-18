from Crypto import Random
from Crypto.Cipher import AES
import random
import hashlib

# 随机生成num字节的密钥
def getPassword(num):
  return bytes([round(random.random() * 255) for x in range(num)])

# 补充bytes类型的data成为128的整数倍
def pad(data):
  if len(data) % 16 == 0:
    return data
  else:
    return data + bytes(16 - (len(data) % 16))

# aes加密
def encrypt_aes(data,password):
  cipher_aes = AES.new(password,AES.MODE_ECB)
  c_data = cipher_aes.encrypt(data)
  return c_data

# aes解密
def decrypt_aes(c_data,password):
  cipher_aes = AES.new(password,AES.MODE_ECB)
  data = cipher_aes.decrypt(c_data)
  return data

#使用python自带的hashlib库
def get_md5_value(data):
  my_md5 = hashlib.md5()#获取一个MD5的加密算法对象
  my_md5.update(data) #得到MD5消息摘要
  my_md5_Digest = my_md5.hexdigest()#以16进制返回消息摘要，32位
  return my_md5_Digest

if __name__ == "__main__":
  password = getPassword(16)
  data = pad("臧海彬".encode("utf8"))
  c_data = encrypt_aes(data,password)
  d_data = decrypt_aes(c_data,password)
  print(data)
  print(c_data)
  print(d_data)
