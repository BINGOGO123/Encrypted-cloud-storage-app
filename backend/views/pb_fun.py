from backend.models import User
from config.config import SUCCESS,ERROR

def judge_user(request):
  if request.method != "POST":
    return {
      "status":ERROR,
      "information":"请求方式错误"
    }
  username = request.POST["username"]
  password = request.POST["password"]
  try:
    user = User.objects.get(username=username)
  except User.DoesNotExist:
    return {
      "status":ERROR,
      "information":"用户不存在"
    }
  if user.password != password:
    return {
      "status":ERROR,
      "information":"密码错误"
    }
  return user