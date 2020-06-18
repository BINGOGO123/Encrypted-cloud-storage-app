from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from backend.models import User,UserAttribute
from config.config import SUCCESS,ERROR
from .pb_fun import judge_user
from django.conf import settings
import ipdb

# 日志类
from config.logger import logger_backend

def get_user_attribute(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response

  # 不是数据所有者
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您没有权限"
    })

  user_information = []
  for one_user in User.objects.all():
    # 跳过数据所有者自身
    if one_user.dataowner == True:
      continue
    user_attribute = {
      "username":one_user.username,
      "attributes":[]
    }
    attributes = UserAttribute.objects.filter(user=one_user)
    for attribute in attributes:
      user_attribute["attributes"].append(attribute.attribute)
    user_information.append(user_attribute)
  
  return JsonResponse({
    "status":SUCCESS,
    "user_information":user_information
  })

def delete_user_attribute(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response

  # 不是数据所有者
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您没有权限"
    })

  operate_username = request.POST["operate_username"]
  attribute = request.POST["attribute"]
  try:
    user_attribute = UserAttribute.objects.get(user__username=operate_username,attribute=attribute)
    user_attribute.delete()
  except UserAttribute.DoesNotExist:
    logger_backend.error("delete_user_attribute 删除的属性或用户不存在 username={} attribute={}".format(operate_username,attribute))
    return JsonResponse({
      "status":ERROR,
      "information":"该用户或属性不存在"
    })
  return JsonResponse({
    "status":SUCCESS
  })

def add_user_attribute(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response

  # 不是数据所有者
  if user.dataowner != True:
    return JsonResponse({
      "status":ERROR,
      "information":"您没有权限"
    })

  operate_username = request.POST["operate_username"]
  attribute = request.POST["attribute"]

  try:
    UserAttribute.objects.get(user__username=operate_username,attribute=attribute)
    return JsonResponse({
      "status":ERROR,
      "information":"该属性已经存在"
    })
  except UserAttribute.DoesNotExist:
    pass
  
  try:
    operate_user = User.objects.get(username=operate_username)
  except User.objects.DoesNotExist:
    logger_backend.error("add_user_attribute 增加属性的用户不存在 username={}".format(operate_username))
    return JsonResponse({
      "status":ERROR,
      "information":"该用户不存在"
    })
  UserAttribute.objects.create(user=operate_user,attribute=attribute)
  return JsonResponse({
    "status":SUCCESS
  })
  
def get_own_attribute(request):
  user_response = judge_user(request)
  if type(user_response) != User:
    return JsonResponse(user_response)
  user = user_response

  attributes = []
  user_attributes = UserAttribute.objects.filter(user=user)
  for user_attribute in user_attributes:
    attributes.append(user_attribute.attribute)
  
  return JsonResponse({
    "status":SUCCESS,
    "attributes":attributes
  })