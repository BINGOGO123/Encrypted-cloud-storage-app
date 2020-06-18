from django.urls import path
from . import views

app_name="secure_encrypt_server"

urlpatterns = [
  path("upload/",views.upload,name="upload"),
  path("upload_ex/",views.upload_ex,name="upload_ex"),
  path("giveup_upload/",views.giveup_upload,name="giveup_upload"),
  path("build_searchable_cloud_syetem/",views.build_searchable_cloud_syetem,name="build_searchable_cloud_syetem"),
  path("search_file/",views.search_file,name="search_file"),
]