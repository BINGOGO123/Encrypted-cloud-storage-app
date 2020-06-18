<template>
  <div class="login">
    <div class="switch">
      <div class="switch-item">
        登录
      </div>
      <div class="switch-item">
        <router-link class="switch-router-link" :to="{name:'register'}" :disabled="logining">
          注册
        </router-link>
      </div>
    </div>
    <div class="line">
      <Tooltip content="25字符以内" placement="top" :transfer="true" class="tip">
        <Input class="input" size="large" v-model.trim="user" maxlength="25" :disabled="logining" placeholder="用户名"/>
      </Tooltip>
    </div>
    <div class="line">
      <Tooltip content="空格无效，30字符以内" placement="top" :transfer="true" class="tip">
        <Input class="input" size="large" type="password" v-model.trim="password" maxlength="30" password :disabled="logining" placeholder="密码"/>
      </Tooltip>
    </div>
    <div class="line line-checkbox">
      <Checkbox class="checkbox" v-model="autoLogin" :disabled="logining">自动登录</Checkbox>
    </div>
    <button class="go" @click="login" :disabled="logining || buttonWait"><Icon type="md-arrow-round-forward" size="40"/></button>
  </div>
</template>

<script>
import config from "../../config.json";

export default {
  name:"Login",
  data:function(){
    return {
      user:"",
      password:"",
      logining:false,
      buttonWait:false,
      autoLogin:false
    };
  },
  methods:{
    login:function(){
      // 2.5s之后才可以再次点击
      this.buttonWait=true;
      setTimeout(()=>{
        this.buttonWait=false;
      },2500);
      if(this.user=="")
      {
        this.$Message.error({
          content:"请输入用户名",
          duration:2.5
        });
        return;
      }
      if(this.password=="")
      {
        this.$Message.error({
          content:"请输入密码",
          duration:2.5
        });
        return;
      }
      this.logining=true;
      const msg = this.$Message.loading({
        content: '正在登录...',
        duration: 0
      });
      let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
      let token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
      let formData = new FormData();
      formData.append("username",this.user);
      formData.append("password",this.password);
      formData.append("autoLogin",this.autoLogin);
      fetch(config.loginInterface,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        msg();
        this.logining=false;
        if(json.status==config.success)
        {
          localStorage.setItem("username",this.user);
          localStorage.setItem("password",this.password);
          this.$Message.success({
            content:"登录成功",
            duration:2.5
          });
          // 跳转到数据所有者界面
          if(json.dataowner)
            this.$router.replace({name:"upload_fun"})
          // 跳转到数据使用者界面
          else
            this.$router.replace({name:"user_search"})
        }
        else
        {
          this.$Message.error({
            content:`登录失败:${json.information}`,
            duration:2.5
          });
        }
      }).catch((error) => {
        msg();
        this.logining = false;
        this.$Message.error({
          content:`登录失败:${error}`,
          duration:2.5
        });
      });
    }
  }
}
</script>

<style scoped lang="scss">
.login
{
  width:330px;
  border-radius:5px;
  box-shadow:0 0px 4px rgb(169, 171, 180);
  padding:10px 15px 10px 15px;
  position:relative;
  z-index:0;
  background-color:white;
}
.switch
{
  display:flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  .switch-item
  {
    font-size:1.3rem;
    padding:10px;
    padding-bottom:5px;
    border-bottom:3px white solid;
    font-weight: bold;
    .switch-router-link
    {
      color:inherit;
    }
  }
  .switch-item:nth-of-type(1)
  {
    border-bottom:3px rgba(120, 139, 221, 0.603) solid;
  }
}
.tip
{
  width:100%;
}
.line
{
  margin-top:15px;
  margin-bottom:15px;
}
.checkbox
{
  font-size:1rem;
  font-weight:bold;
  color:rgb(109, 148, 221);
}
.line-checkbox
{
  display:flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top:0;
  margin-bottom:5px;
}
.go
{
  border:none;
  outline:none;
  font-size:1.2rem;
  font-weight:bold;
  width:65px;
  height:65px;
  line-height:75px;
  border-radius:100px;
  text-align:center;
  background-color:rgba(120, 139, 221, 0.603);
  box-shadow:0 0 6px rgba(120, 139, 221, 0.603);
  color:white;
  cursor:pointer;
  position:absolute;
  bottom:-90px;
  left:130px;
  -webkit-user-select: none;
}
.go:active
{
  background-color:rgb(120, 139, 221);
}
.input /deep/ .ivu-input
{
  background-color:rgba(255, 255, 255, 0.692) !important;
  // color:black;
}
.password_error /deep/ .ivu-input
{
  color:red;
}
</style>