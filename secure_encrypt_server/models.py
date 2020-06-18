from django.db import models

# Create your models here.

class SecureFile(models.Model):
  secure_file = models.ImageField(upload_to="secure_file",null=False,blank=False)
  date = models.DateTimeField(auto_now=True)
  # 权限表达式
  ex = models.CharField(max_length=200,null=True,blank=True)
  # 该文件的md5值，防止上传重复文件
  md5 = models.CharField(max_length=50,null=False,blank=False)
  def __str__(self):
    return str(self.date) + self.secure_file.name

# 用以标记同一批次上传的文件
class Label(models.Model):
  label = models.CharField(max_length=1000,null=False,blank=False)

  def __str__(self):
    return self.label