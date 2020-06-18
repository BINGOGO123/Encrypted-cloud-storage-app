<template>
  <div class="data-user-fun">
    <keep-alive>
      <router-view class="view"
      :builded="builded"
      @re_get_secret_search="re_get_secret_search"
      :get_secret_search.sync="get_secret_search"
      ></router-view>
    </keep-alive>
    <AppMenu
    :menu="menu"
    :now="active"
    class="app-menu"
    ></AppMenu>
  </div>
</template>

<script>
import AppMenu from "../appmenu/AppMenu.vue";
import config from "../config.json";

export default {
  name:"DataUserFun",
  components:{
    AppMenu
  },
  data:function(){
    return {
      menu:[
        {
          to:{name:"user_search"},
          icon:"md-search",
          title:"文件查找",
          name:"user_search"
        },
        {
          to:{name:"user_user_information"},
          icon:"md-contact",
          title:"个人信息",
          name:"user_user_information"
        }
      ],
      builded:false,
      get_secret_search:false
    };
  },
  computed:{
    active:function(){
      let name = this.$route.name;
      for(let i = 0;i<this.menu.length;i++)
        if(this.menu[i].name == name)
          return i;
      return 0;
    }
  },
  created:function(){
    // 为了测试
    // document.cookie="searchable_encryption_username=bingo";
    // document.cookie="searchable_encryption_password=a123";
    
    this.query();
  },
  methods:{
    query:function(){
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
      formData.append("username",username);
      formData.append("password",password);
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
          this.builded = json.builded;
          if(json.dataowner==true)
            this.$router.replace({name:"upload_fun"});
        }
        else
          this.$router.replace({name:"login"});
      }).catch(()=>{
        this.$Message.error({
          content:"出现错误，请重新登录",
          duration:2.5
        });
        this.$router.replace({name:"login"});
      });
    },
    // 仅通知搜索页面重新获取密钥
    re_get_secret_search:function(){
      this.get_secret_search=true;
    }
  }
}
</script>

<style scoped lang="scss">
.data-user-fun
{
  height:100%;
  display:flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: stretch;
  .view
  {
    flex:1;
  }
  background-color:#f5f5f5;
}
.app-menu
{
  box-shadow:0 0 4px rgb(200,200,200);
  width:100%;
}
</style>