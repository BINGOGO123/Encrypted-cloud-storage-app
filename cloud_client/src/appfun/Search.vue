<template>
  <div class="search">
    <div class="search-input">
      <Input class="searh-input-input" v-model.trim="searchInfo" :disabled="!builded || secret==null || loading==true" search placeholder="关键词以空格相隔" size="large" maxlength="100" @keyup.native.13="go_search" />
    </div>
    <div class="card" v-if="!builded">
      可搜索云存储系统尚未建立
    </div>
    <div class="card error" v-else-if="error_secret==true">
      密钥不合法，请先更改密钥
    </div>
    <div class="card" v-else-if="secret==null">
      当前设备中无密钥，请先添加密钥
    </div>
    <!-- 一切正常，系统已经建立，并且有合法的密钥 -->
    <template v-else>
      <!-- 显示所有关键词 -->
      <div class="card all-criticals">
        <b class="criticals">可选关键词（点击加入搜索）：</b>
        <br/>
        <div class="tag-list">
          <Tag v-for="(one,index) in secret.word" :key="'a'+index" class="tag">
            <span @click="addTag(one)">{{one}}</span>
          </Tag>
        </div>
      </div>
      <!-- 只有开始搜索过才显示下面的内容，即至少搜索过一次 -->
      <template v-if="searched">
        <!-- 加载中 -->
        <div class="card" v-if="loading">
          <Spin v-if="loading" class="left-spin"><Icon type="ios-loading" size=15 class="spin"></Icon> 正在查询..</Spin>
        </div>
        <!-- 出现错误 -->
        <div class="card error" v-else-if="information != ''">
          {{information}}
        </div>
        <template v-else>
          <div class="card">
            <b class="criticals">当前搜索关键词：</b>
            <br />
            <Tag v-for="(critical,index) in criticals" :key="'t'+index" type="border" class="tag">
              {{critical}}
            </Tag>
          </div>
          <div class="card file-item" v-for="(item,index) in file_list" :key="index">
            <div class="file-name">
              {{item.name}}
            </div>
            <ButtonGroup class="button-group">
              <Button @click="item.display=1" long>查看密文</Button>
              <Button @click="item.display=2" long>查看明文</Button>
              <Button v-show="item.display!=0" @click="item.display=0" long>关闭</Button>
            </ButtonGroup>
            <pre v-show="item.display==1" class="preview">{{item.encrypt_text}}</pre>
            <pre v-show="item.display==2" class="preview">{{item.text}}</pre>
          </div>
        </template>
      </template>
    </template>

  </div>
</template>

<script>
import config from "../config.json";
import {decode} from "../byte_str.js";

export default {
  name:"Search",
  props:{
    builded:Boolean,
    get_secret_search:Boolean
  },
  data:function(){
    return {
      searchInfo:"",
      token:null,
      password:null,
      username:null,
      secret:null,
      error_secret:false,
      file_list:[],
      error_info:"",
      loading:false,
      criticals:null,
      // 是否搜索过一次
      searched:false
    }
  },
  computed:{
    information:function(){
      if(this.error_info!="")
        return this.error_info;
      else if(this.file_list.length <= 0)
        return "未搜索到相关文件";
      return "";
    }
  },
  methods:{
    go_search:function(){
      // 如果搜索空内容，则直接返回，不提示
      if(this.searchInfo == "")
        return;

      this.searched=true;

      // 表示正在搜索中
      this.loading=true;

      // 取出所有关键词
      let criticals = this.searchInfo.split(" ");
      let location;
      for(;;)
      {
        location = criticals.indexOf("");
        if(location == -1)
          break
        criticals.splice(location,1)
      }
      this.criticals = criticals;

      // 生成查询向量
      let query_vector = new Array(this.secret.word.length);
      for(let i = 0;i<query_vector.length;i++)
      {
        if(criticals.indexOf(this.secret.word[i]) != -1)
          query_vector[i] = 1;
        else
          query_vector[i] = 0;
      }

      // 用矩阵乘以向量
      let tw = this.dot(this.secret.decrypt_matrix,query_vector);

      // 表单数据
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("tw",tw);
      formData.append("aes_secret",this.secret.aes_secret);

      // 发送http请求
      fetch(config.search_file,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":this.token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        this.loading=false;
        if(json.status==config.success)
        {
          this.error_info=""
          this.file_list = json.file_list;
        }
        else
          this.error_info = json.information;
      }).catch((error)=>{
        this.loading=false;
        this.error_info=error;
      });
    },
    // 矩阵乘以向量
    dot:function(matrix,vector)
    {
      let result = [];
      for(let line of matrix)
      {
        let count = 0;
        for(let i = 0;i<vector.length;i++)
          count += (vector[i] * line[i]);
        result.push(count);
      }
      return result;
    },
    addTag:function(name)
    {
      if(this.searchInfo.split(" ").indexOf(name) == -1)
        this.searchInfo = this.searchInfo + " " + name;
    }
  },
  created:function(){
    // 必要参数
    // let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
    // this.token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_username=([^;.]*).*$/; // 用于从cookie中匹配username值
    // this.username = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_password=([^;.]*).*$/; // 用于从cookie中匹配username值
    // this.password = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    this.token = null;
    this.password = localStorage.getItem("password");
    this.username = localStorage.getItem("username");

    // 从设备中查看是否存在密钥
    if(localStorage.getItem("secret"))
    {
      let secret;
      this.error_secret=false;
      try {
        secret = localStorage.getItem("secret");
        secret = decode(secret);
        this.secret = JSON.parse(secret);
      }
      catch {
        this.secret = null;
        this.error_secret = true;
      }
    }
    else
    {
      this.secret = null;
      this.error_secret = false;
    }
  },
  watch:{
    // 更新密钥
    get_secret_search:function(newValue)
    {
      if(!newValue)
        return;
      
      // 更新密钥
      if(localStorage.getItem("secret"))
      {
        let secret;
        this.error_secret=false;
        try {
          secret = localStorage.getItem("secret");
          secret = decode(secret);
          this.secret = JSON.parse(secret);
        }
        catch {
          this.secret = null;
          this.error_secret = true;
        }
      }
      else
      {
        this.secret=null;
        this.error_secret=false;
      }
      
      // 更新密钥之后初始化所有信息
      this.searchInfo = "";
      this.file_list = [];
      this.error_info = "";
      this.searched = false;
      this.criticals = null;
      this.$emit("update:get_secret_search",false);
    }
  }
}
</script>

<style scoped lang="scss">
.search
{
  padding:15px 15px 0 15px;
}
.search-input
{
  margin-bottom:15px;
  font-size:1rem;
  .searh-input-input /deep/ input
  {
    border-radius:100px;
    padding-left:10px;
    font-size:1rem;
  }
}
.card
{
  border-radius:5px;
  box-shadow:0 2px 2px rgb(200,200,200);
  padding:10px 15px 10px 15px;
  position:relative;
  z-index:0;
  background-color:white;
  font-size:1rem;
  margin-bottom:15px;
}
.spin{
  animation: ani-spin 1s linear infinite;
}
@keyframes ani-spin {
  from { transform: rotate(0deg);}
  50%  { transform: rotate(180deg);}
  to   { transform: rotate(360deg);}
}
.left-spin
{
  text-align:left;
}
.tag
{
  word-break:break-all;
}
.tag-list
{
  max-height:150px;
  overflow-y:scroll;
  overflow-x:hidden;
}
.success
{
  color:#19be6b;
}
.error
{
  color:#ed4014;
}
.preview
{
  margin-top:6px;
  max-height:100px;
  overflow-y:scroll;
  overflow-x:hidden;
  font-size:0.8rem;
  word-break:break-all;
  white-space: pre-wrap;
}
.file-name
{
  font-weight:bold;
}
.button-group
{
  display:flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-top:3px;
  flex:1;
}
.criticals
{
  // color:#2d8cf0;
}
</style>