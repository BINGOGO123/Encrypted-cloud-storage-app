from django.urls import path
from .views import account,user_attribute

app_name="backend"

urlpatterns = [
  path("login/",account.login,name="login"),
  path("register/",account.register,name="register"),
  path("login_confirm/",account.login_confirm,name="login_confirm"),
  path("logout/",account.logout,name="logout"),
  path("get_user_attribute/",user_attribute.get_user_attribute,name="get_user_attribute"),
  path("delete_user_attribute/",user_attribute.delete_user_attribute,name="delete_user_attribute"),
  path("add_user_attribute/",user_attribute.add_user_attribute,name="add_user_attribute"),
  path("get_own_attribute/",user_attribute.get_own_attribute,name="get_own_attribute"),
]