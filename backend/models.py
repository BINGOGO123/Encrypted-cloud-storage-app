from django.db import models
from django.utils import timezone

# 用户的注册信息
class User(models.Model):
  password = models.CharField(max_length=50,null=False)
  username = models.CharField(max_length=90,primary_key=True)
  register_date = models.DateField(auto_now=True)
  # 是否为数据拥有者
  dataowner = models.BooleanField(default=False)

  def __str__(self):
    return self.username

# 数据使用者的属性表
class UserAttribute(models.Model):
  user = models.ForeignKey(User,on_delete=models.CASCADE)
  attribute = models.CharField(max_length=100,null=False,blank=False)
  def __str__(self):
    return self.user.__str__()

# 数据所有者上传的文件
class EncryptFile(models.Model):
  encrypt_file = models.FileField(upload_to="encrypt_file",null=False,blank=False)
  encrypt_vector = models.TextField(null=False,blank=False)
  permission = models.CharField(max_length=1000,null=True,blank=True)
  upload_date = models.DateTimeField(auto_now=True)

  def __str__(self):
    return str(self.upload_date) + self.encrypt_file.name
