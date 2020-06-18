<template>
  <div class="register">
    <div class="switch">
      <div class="switch-item">
        <router-link class="switch-router-link" :to="{name:'login'}" :disabled="registering">
          登录
        </router-link>
      </div>
      <div class="switch-item">
        注册
      </div>
    </div>
    <div class="line">
      <Tooltip content="25字符以内" placement="top" :transfer="true" class="tip">
        <Input class="input" size="large" v-model.trim="user" maxlength="25" placeholder="用户名" :disabled="registering"/>
      </Tooltip>
    </div>
    <div class="line">
      <Tooltip content="空格无效，30字符以内" placement="top" :transfer="true" class="tip">
        <Input class="input" size="large" type="password" password v-model.trim="password" maxlength="25" placeholder="密码" :disabled="registering"/>
      </Tooltip>
    </div>
    <div class="line">
      <Input :class="{'input':true,'password_error':password_error}" size="large" type="password" password v-model.trim="ensure_password" maxlength="25" placeholder="确认密码" :disabled="registering"/>
    </div>
    <button class="go" @click="register" :disabled="registering || buttonWait"><Icon type="md-arrow-round-forward" size="40"/></button>
  </div>
</template>

<script>
import config from "../../config.json";

export default {
  name:"Register",
  data:function(){
    return {
      user:"",
      password:"",
      ensure_password:"",
      registering:false,
      buttonWait:false
    };
  },
  computed:
  {
    password_error:function(){
      if(this.ensure_password != "" && this.ensure_password != this.password)
        return true;
      return false;
    }
  },
  methods:{
    register:function(){
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
      if(this.ensure_password=="")
      {
        this.$Message.error({
          content:"请输入确认密码",
          duration:2.5
        });
        return;
      }
      if(this.password!=this.ensure_password)
      {
        this.$Message.error({
          content:"两次输入密码不一致",
          duration:2.5
        });
        return;
      }
      this.registering=true;
      const msg = this.$Message.loading({
        content: '正在注册...',
        duration: 0
      });
      let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
      let token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
      let formData = new FormData();
      formData.append("username",this.user);
      formData.append("password",this.password);
      fetch(config.registerInterface,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        msg();
        this.registering = false;
        if(json.status==config.success)
        {
          this.$Message.success({
            content:"注册成功",
            duration:2.5
          });
          this.$router.push({name:"login"});
          // 复原状态
          this.password="";
          this.ensure_password="";
          this.user="";
        }
        else
        {
          this.$Message.error({
            content:`注册失败:${json.information}`,
            duration:2.5
          });
        }
      }).catch((error) => {
        msg();
        this.registering = false;
        this.$Message.error({
          content:`注册失败:${error}`,
          duration:2.5
        });
      });
    }
  }
}
</script>

<style scoped lang="scss">
.register
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
  .switch-item:nth-of-type(2)
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