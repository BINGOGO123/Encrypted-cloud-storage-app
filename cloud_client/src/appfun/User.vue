<template>
  <div class="user">
    <div v-if="!loaded" class="card">
      <Spin><Icon type="ios-loading" size=15 class="spin"></Icon> 用户属性加载中..</Spin>
    </div>
    <div v-else-if="information != null" class="card">
      {{information}}
    </div>
    <div v-else class="card" v-for="(user_attribute,index) in user_information" :key="index">
      <div class="name">
        {{user_attribute.username}}
      </div>
      <div class="attributes">
        <Tag v-for="(attribute,index1) in user_attribute.attributes"
        :key="'a'+index1"
        closable
        @on-close="deleteAttribute(user_attribute.username,attribute)"
        size="medium"
        class="tag">
        {{attribute}}</Tag>
        <Button class="button" icon="md-add" type="dashed" @click="getAttribute(user_attribute.username)">增加属性</Button>
      </div>
    </div>
    <Modal
    :closable="false"
    v-model="modal">
      <div slot="header" class="modal-header normal-font">
        <Icon type="md-paper" /> 请输入属性值
      </div>
      <div slot="default" class="normal-font">
        <Input v-model.trim="attribute" placeholder="20字以内" :maxlength="20"/>
      </div>
      <div slot="footer">
        <Button @click="ok" :disabled="ok_wait">确定</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
import config from "../config.json";
import {contain_special} from "../tools.js";

export default {
  name:"User",
  created:function(){
    let formData = new FormData()
    // let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
    // let token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_username=([^;.]*).*$/; // 用于从cookie中匹配username值
    // let username = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_password=([^;.]*).*$/; // 用于从cookie中匹配username值
    // let password = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    let token = null;
    let password = localStorage.getItem("password");
    let username = localStorage.getItem("username");
    // 未处于登录状态
    if(username == null || password == null)
    {
      this.$router.replace({name:"login"});
      return;
    }
    this.username = username;
    this.password = password;
    this.token = token;
    formData.append("username",username);
    formData.append("password",password);
    fetch(config.get_user_attribute,{
      method:"POST",
      body:formData,
      headers:{
        "X-CSRFToken":token
      }
    }).then(function(response){
      return response.json();
    }).then((json) => {
      if(json.status==config.success)
        this.user_information = json.user_information;
      else
        this.error_info = json.information;
      this.loaded=true;
    }).catch((error)=>{
      this.error_info = error;
      this.loaded=true;
    });
  },
  data:function(){
    return {
      user_information:[],
      error_info:"",
      loaded:false,
      username:null,
      password:null,
      token:null,
      modal:false,
      attribute:"",
      add_username:null,
      ok_wait:false
    };
  },
  methods:{
    deleteAttribute:function(username,attribute)
    {
      const msg = this.$Message.loading({
        content: '正在删除属性...',
        duration: 0
      });
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("operate_username",username);
      formData.append("attribute",attribute);
      fetch(config.delete_user_attribute,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":this.token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        msg();
        if(json.status==config.success)
        {
          // 从user_information中删除
          for(let i = 0;i<this.user_information.length;i++)
            if(this.user_information[i].username==username)
            {
              let location = this.user_information[i].attributes.indexOf(attribute);
              if(location != -1)
                this.user_information[i].attributes.splice(location,location+1);
            }
          this.$Message.success({
            content: '删除成功',
            duration: 2
          });
        }
        else
        {
          this.$Message.error({
            content: `删除失败:${json.information}`,
            duration: 2
          });
        }
      }).catch((error)=>{
        msg();
        this.$Message.error({
          content: `删除失败:${error}`,
          duration: 2
        });
      });
    },
    addAttribute:function(username,attribute)
    {
      const msg = this.$Message.loading({
        content: '正在添加属性...',
        duration: 0
      });
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("operate_username",username);
      formData.append("attribute",attribute);
      fetch(config.add_user_attribute,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":this.token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        msg();
        if(json.status==config.success)
        {
          // 从user_information中增加
          for(let i = 0;i<this.user_information.length;i++)
            if(this.user_information[i].username==username)
              this.user_information[i].attributes.push(attribute);
          this.$Message.success({
            content: '添加成功',
            duration: 2
          });
        }
        else
        {
          this.$Message.error({
            content: `添加失败:${json.information}`,
            duration: 2
          });
        }
      }).catch((error)=>{
        msg();
        this.$Message.error({
          content: `添加失败:${error}`,
          duration: 2
        });
      });
    },
    getAttribute:function(username)
    {
      this.add_username = username;
      this.modal = true;
    },
    ok:function(){
      if(this.attribute == "")
      {
        // 2s之后才可以再次点击
        this.ok_wait=true;
        setTimeout(()=>{
          this.ok_wait=false;
        },2000);
        this.$Message.error({
          content: `属性不能为空`,
          duration: 2
        });
        return;
      }
      else if(contain_special(this.attribute))
      {
        // 2s之后才可以再次点击
        this.ok_wait=true;
        setTimeout(()=>{
          this.ok_wait=false;
        },2000);
        this.$Message.error({
          content: `包含空格或非法符号`,
          duration: 2
        });
        return;
      }
      this.modal = false;
      this.addAttribute(this.add_username,this.attribute);
    }
  },
  computed:{
    information:function(){
      if(this.error_info != "")
        return this.error_info;
      else if(this.user_information.length <= 0)
        return "目前没有其他用户";
      else
        return null;
    }
  }
}
</script>

<style scoped lang="scss">
.user
{
  overflow-y:scroll;
  padding:15px 15px 0 15px;
}
.card
{
  border-radius:5px;
  // border-radius:0 0 5px 5px;
  box-shadow:0 2px 2px rgb(200,200,200);
  padding:10px 15px 10px 15px;
  position:relative;
  z-index:0;
  background-color:white;
  font-size:1rem;
  margin-bottom:15px;
}
.name
{
  font-size:1rem;
  font-weight: bold;
  // border-bottom:2px rgba(120, 139, 221, 0.603) solid;
  border-bottom:2px #2d8cf0 solid;
  display:inline-block;
  margin-bottom:8px;
}
.tag
{
  font-size:0.9rem;
  height:28px;
  line-height: 26px;
}
.button
{
  height:28px;
  line-height: 26px;
  font-size:0.9rem;
}
// 加载动画
.spin{
  animation: ani-spin 1s linear infinite;
}
@keyframes ani-spin {
  from { transform: rotate(0deg);}
  50%  { transform: rotate(180deg);}
  to   { transform: rotate(360deg);}
}
.modal-header
{
  text-align: center;
  font-size:1rem;
}
.normal-font
{
  font-size:1rem;
}
</style>