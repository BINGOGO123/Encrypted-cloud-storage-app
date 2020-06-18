<template>
  <div class="account">
    <div class="label">
      <router-link :to="{'name':'login'}" v-if="dataowner">数据使用者</router-link>
      <div class="now" v-else>
        数据使用者
      </div>
      <div>
        |
      </div>
      <router-link :to="{'name':'dataowner'}" v-if="!dataowner">数据所有者</router-link>
      <div class="now" v-else>
        数据所有者
      </div>
    </div>
    <div class="region">
      <transition name="account">
        <keep-alive>
          <router-view class="display"></router-view>
        </keep-alive>
      </transition>
    </div>
  </div>
</template>

<script>
import config from "../config.json";

export default {
  name:"Account",
  computed:{
    dataowner:function(){
      if(this.$route.name=="dataowner")
        return true;
      else
        return false;
    }
  },
  beforeCreate:function(){
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
      return;
    formData.append("username",username);
    formData.append("password",password);
    console.log(username,password)
    fetch(config.login_confirm,{
      method:"POST",
      body:formData,
      headers:{
        "X-CSRFToken":token
      }
    }).then(function(response){
      return response.json();
    }).then((json) => {
      if(json.status==config.success)
      {
        console.log(json);
        if(json.dataowner==true)
          this.$router.replace({name:"upload_fun"});
        else
          this.$router.replace({name:"user_search"});
      }
    });
  }
};
</script>

<style scoped lang="scss">
*
{
  -webkit-user-select: none;
}
.account
{
  display:flex;
  flex-direction: column;
  align-items:center;
  justify-content: flex-start;
  height:100%;
  overflow:hidden;
  background-color:#f1f2f9;
  // background-color:#ededed;
}
.region
{
  position:relative;
  // width:360px;
  margin-top:20px;
}
.account-enter-active
{
  transition:all 1s;
}
.account-enter
{
  opacity:0;
  /* display:none; */
}
.account-enter-to
{
  opacity:1;
  /* display:block; */
}

.label
{
  width:330px;
  border-radius:5px;
  box-shadow:0 0px 4px rgb(169, 171, 180);
  padding:10px 15px 10px 15px;
  position:relative;
  background-color:white;
  margin-top:20px;
  display:flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  font-size:1.1rem;
}
.now
{
  font-weight:bold;
  color:#2d8cf0;
}
</style>