<template>
  <div class="data-owner-fun">
    <!-- <div class="app-name">用户管理</div> -->
    <keep-alive>
      <router-view class="view"
      :builded="builded"
      @query="query"
      @re_get_secret="re_get_secret"
      @re_get_secret_search="re_get_secret_search"
      :get_secret.sync="get_secret"
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
  name:"DataOwnerFun",
  components:{
    AppMenu
  },
  data:function(){
    return {
      menu:[
        {
          to:{name:"search"},
          icon:"md-search",
          title:"文件查找",
          name:"search"
        },
        {
          to:{name:"user"},
          icon:"md-grid",
          title:"用户管理",
          name:"user"
        },
        {
          to:{name:"upload_fun"},
          icon:"md-cloud-upload",
          title:"上传",
          name:"upload_fun"
        },
        {
          to:{name:"user_information"},
          icon:"md-contact",
          title:"个人信息",
          name:"user_information"
        }
      ],
      builded:false,
      get_secret:false,
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
    // document.cookie="searchable_encryption_username=dataowner";
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
          if(json.dataowner==false)
            this.$router.replace({name:"user_search"});
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
    // 通知另外的界面重新获取密钥
    re_get_secret:function(){
      this.get_secret=true;
      this.get_secret_search=true;
    },
    // 仅通知搜索页面重新获取密钥
    re_get_secret_search:function(){
      this.get_secret_search=true;
    }
  }
}
</script>

<style scoped lang="scss">
.data-owner-fun
{
  height:100%;
  display:flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: stretch;
  .view
  {
    flex:1;
    overflow-y:scroll;
    overflow-x:hidden;
  }
  background-color:#f5f5f5;
  // max-width:500px;
  // margin-left:auto;
  // margin-right:auto;
  .app-name
  {
    height:60px;
    line-height: 60px;
    // background-color:#2d8cf0;
    // color:white;
    // background-color:#f1f2f9;
    font-size:1.3rem;
    font-weight:bold;
    text-align: center;
    text-align:left;
    padding-left:20px;
    box-shadow:0 0 4px rgb(200,200,200);
  }
}
.app-menu
{
  box-shadow:0 0 4px rgb(200,200,200);
  width:100%;
}
</style>