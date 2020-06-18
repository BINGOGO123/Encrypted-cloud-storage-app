import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# 这里记录了django操作的精髓部分，我花了很久才搞明白

# 通过Bytes对象生成一个django.core.files.uploadedfile.InMemoryUploadedFile对象，这里限定是文本文件，也就是text/plain类型
def getInMemoryUploadedFile_bytes(data,target_filename):
  pic_io = BytesIO()
  size = pic_io.write(data)
  
  pic_file = InMemoryUploadedFile(
    file=pic_io,
    field_name=None,
    name=target_filename,
    content_type="text/plain",
    # 对于文件这种方法也可
    # size=os.path.getsize(filename),
    size=size,
    charset=None
  )
  return pic_file

# 通过filename生成一个django.core.files.uploadedfile.InMemoryUploadedFile对象，这里限定是文本文件，也就是text/plain类型
def getInMemoryUploadedFile_file(filename,target_filename):
  f = open(filename,"rb")
  data = f.read()
  f.close()

  return getInMemoryUploadedFile_bytes(data,target_filename)
