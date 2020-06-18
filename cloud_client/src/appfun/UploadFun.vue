<template>
  <div class="upload-fun">
    <div class="card" v-if="builded">
      当前已经生成了可搜索云存储系统。<br/><router-link :to="{name:'search'}">前往搜索</router-link>
    </div>
    <div v-else class="card">
      当前尚未生成可搜索云存储系统。
    </div>
    <Modal
    :closable="false"
    v-model="secret_modal">
      <div slot="default">
        <div class="normal-font center">
          <Icon type="ios-checkmark-circle" size="16" class="success"/> 生成成功，密钥已存储在当前设备
          <br/>
        </div>
        <div class="secret">{{secret.slice(0,35) + "..."}}</div>
      </div>
      <div slot="footer">
        <Button long 
        v-clipboard:copy="secret"
        v-clipboard:success="copy_success"
        v-clipboard:error="copy_error">
          复制密钥
        </Button>
      </div>
    </Modal>
    <Modal
    :closable="false"
    v-model="giveup_modal">
      <div slot="default">
        <div class="normal-font center">
          <Icon type="md-alert" size="16" class="error"/> 这将删除已经提交的文件，是否确认？
        </div>
      </div>
      <div slot="footer">
        <Button @click="giveup_ok" type="error">确认</Button>
        <Button @click="giveup_modal=false">取消</Button>
      </div>
    </Modal>
    <Modal
    :closable="false"
    v-model="submit_modal">
      <div slot="default">
        <div class="normal-font center">
          <Icon type="md-alert" size="16" class="error" /> 这将删除之前的文件系统，是否确认？
        </div>
      </div>
      <div slot="footer">
        <Button @click="submit_ok" type="primary">确认</Button>
        <Button @click="submit_modal=false">取消</Button>
      </div>
    </Modal>
    <Button v-if="!start_upload" type="primary" long class="button margin-bottom" size="large" @click="change_upload(true)">
      <Icon type="ios-cloud-upload-outline" size="18"></Icon>
      <template v-if="builded">
        重新生成文件系统
      </template>
      <template v-else>
        生成文件系统
      </template>
    </Button>
    <template v-else>
      <div class="card relative">
        <div class="upload-file-display" v-if="upload_file_list.length > 0">
          <div class="help">
            <Tooltip placement="left-start">
              <Icon type="md-help-circle" size="20"/>
                <div slot="content" style="width:200px;word-break:break-all;white-space: pre-wrap;">
                  <p>权限表达式规则:由用户属性和& | ! ( )组成的表达式。</p>
                  <p>例如:<b>(教师&good)|!apple</b></p>
              </div>
            </Tooltip>
          </div>
          <div v-for="(item,index) in upload_file_list" :key="index">
            <Spin class="left-spin" v-if="!item.uploaded"><Icon type="ios-loading" size=15 class="spin"></Icon> {{item.name}} 加载中</Spin>
            <!-- 必须uploaded才会显示下面的东西 -->
            <template v-else>
              <div class="upload-file-base-info">
                <div class="file-name">
                  <b>{{item.name}}</b>
                </div>
              </div>
              <div class="detail-info">
                <template v-if="item.error_info!=''">
                  <div class="upload-error">
                    {{item.error_info}}
                  </div>
                  <Button @click="re_upload_file(item)" :disabled="loading">重新加载</Button>
                </template>
                <template v-else>
                  <Tooltip content="150字符以内" placement="top" :transfer="true" class="tip">
                    <Input placeholder="权限表达式" :disabled="loading" v-model.trim="item.ex" :class="{error_ex:check_ex(item.ex)!=true}" :maxlength="150" @change.native="submit_ex(item)" />
                  </Tooltip>
                  <Button v-if="!item.display" @click="preview(item)">预览</Button>
                  <Button v-else @click="preview_cancel(item)">取消预览</Button>
                </template>
              </div>
              <Spin v-if="item.display && !item.loaded" class="left-spin" style="margin-top:6px;"><Icon type="ios-loading" size=15 class="spin"></Icon> 正在加载...</Spin>
              <pre class="preview" v-else-if="item.display">{{item.text}}</pre>
            </template>
            <Divider class="divider" />
          </div>
        </div>
        <div class="menu">
          <Upload
          class="upload"
          action=""
          multiple
          :show-upload-list="false"
          :before-upload="addItem">
            <Button type="dashed" :disabled="loading"><Icon type="ios-cloud-upload-outline" size="18"></Icon> 点击提交文件</Button>
          </Upload>
          <Button class="button" :disabled="loading" type="primary" @click="start_giveup_modal">放弃</Button>
        </div>
      </div>
      <Button 
      type="primary" 
      long 
      class="button margin-bottom" 
      size="large" 
      @click="start_submit_modal"
      :loading="loading"
      v-if="upload_file_list.length>0">
        提 交
      </Button>
    </template>
  </div>
</template>

<script>
import config from "../config.json";
import {encode} from "../byte_str.js";
import {contain_special_but_logic} from "../tools.js";

export default {
  name:"UploadFun",
  props:{
    builded:Boolean
  },
  created:function()
  {
    // let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
    // this.token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_username=([^;.]*).*$/; // 用于从cookie中匹配username值
    // this.username = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    // regex = /.*searchable_encryption_password=([^;.]*).*$/; // 用于从cookie中匹配username值
    // this.password = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
    this.token = null;
    this.password = localStorage.getItem("password");
    this.username = localStorage.getItem("username");
    // 标识同一批文件
    this.label = this.getLabel();
  },
  data:function(){
    return {
      // 定义最大文件数目和单个文件的大小（单位KB）
      max_file_number:200,
      max_file_size:2048,
      fomatter:["txt","c","cpp","py","js","css","html","vue","json"],
      label:null,
      password:null,
      username:null,
      token:null,
      start_upload:false,
      upload_file_list:[],
      giveup_modal:false,
      submit_modal:false,
      secret_modal:false,
      loading:false,
      secret:""
    }
  },
  methods:{
    getLabel:function(){
      // 标识同一批文件
      let label = [];
      for(let i = 0; i < 100; i++)
        label.push(String.fromCharCode(Math.floor(Math.random() * 26 + 97)));
      return label.join("");
    },
    change_upload:function(value){
      this.start_upload = value;
    },
    addItem:function(file){
      if(this.upload_file_list.length >= this.max_file_number)
      {
        this.$Message.error({
          content:"最多上传" + this.max_file_number + "个文件",
          duration:2
        });
        return false;
      }
      // 格式错误
      if(this.fomatter.indexOf(file.name.split(".").pop().toLowerCase())==-1)
      {
        this.$Message.error({
          content:"请上传文本文件",
          duration:2
        });
        return false;
      }
      // 太大
      if(file.size > this.maxSize)
      {
        this.$Message.error({
          content:"上传文件不能超过" + this.maxSize/1024 + "M",
          duration:2
        });
        return false;
      }
      // 将文件加入显示列表中
      let item = {
        file:file,
        name:file.name,
        uploaded:false,
        display:false,
        error_info:"",
        ex:"",
        loaded:false
      };
      this.upload_file_list.push(item);
      this.upload_file(item);
      return false;
    },
    upload_file:function(item)
    {
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("file",item.file);
      formData.append("label",this.label);
      fetch(config.secure_encrypt_server,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":this.token
        }
      }).then(function(response){
        return response.json();
      }).then((json) => {
        if(json.status==config.success)
        {
          item.uploaded=true;
          item.file_id = json.id;
        }
        else
        {
          item.uploaded=true;
          item.error_info=json.information;
        }
      }).catch(()=>{
        item.uploaded=true;
        item.error_info="文件加载失败";
      });
    },
    re_upload_file:function(item)
    {
      item.uploaded=false;
      item.error_info=""
      this.upload_file(item);
    },
    submit_ex:function(item)
    {
      console.log(arguments);
      let check = this.check_ex(item.ex);
      // 表达式不合法
      if(check != true)
      {
        this.$Message.error({
          content:check,
          duration:2
        });
        return;
      }
      let msg = this.$Message.loading({
        content:"更改中...",
        duration:0
      });
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("ex",item.ex);
      formData.append("file_id",item.file_id);
      fetch(config.upload_ex,{
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
          this.$Message.success({
            content:"更改成功",
            duration:2
          });
        }
        else
        {
          this.$Message.error({
            content:"更改失败",
            duration:2
          });
        }
      }).catch(()=>{
        msg();
        this.$Message.error({
          content:"更改失败",
          duration:2
        });
      });
    },
    check_ex:function(ex)
    {
      // 空字符串合法
      if(ex.length <= 0)
        return true;
      if(contain_special_but_logic(ex))
        return "包含非法符号";
      
      // 去掉所有空白符
      // ex = ex.replace(/\s/g,"");
      // if(ex.length <= 0)
      //   return true;
      
      // 将&|!()\s之外的符号替换为0
      ex = ex.replace(/[^\s&|!()]+/g,"0");
      // 如果不构成一个表达式则说明格式不对
      try {
        eval(ex);
      } catch {
        return "格式错误";
      }
      return true;
    },
    start_giveup_modal:function()
    {
      if(this.upload_file_list.length > 0)
        this.giveup_modal = true;
      else
        this.change_upload(false);
    },
    start_submit_modal:function()
    {
      if(this.builded)
        this.submit_modal=true;
      else
        this.submit_ok();
    },
    submit_ok:function(){
      this.submit_modal = false;
      this.loading=true;
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("label",this.label);
      fetch(config.build_searchable_cloud_syetem,{
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
          this.upload_file_list = [];
          // 重新生成label
          this.label = this.getLabel();
          this.change_upload(false);
          this.$emit("query");
          this.$emit("re_get_secret");
          this.secret = encode(JSON.stringify(json.secret));
          localStorage.setItem("secret",this.secret);
          this.secret_modal = true;
        }
        else
        {
          this.loading=false;
          this.$Message.error({
            content:"生成失败",
            duration:2
          });
        }
      }).catch((error)=>{
        this.loading=false;
        this.$Message.error({
          content:`异常生成失败${error}`,
          duration:2
        });
      });
    },
    giveup_ok:function(){
      this.giveup_modal = false;
      let msg = this.$Message.loading({
        content:"正在删除...",
        duration:0
      });
      let formData = new FormData();
      formData.append("username",this.username);
      formData.append("password",this.password);
      formData.append("label",this.label);
      fetch(config.giveup_upload,{
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
          this.$Message.success({
            content:"删除成功",
            duration:2
          });
          this.upload_file_list = []
          this.change_upload(false);
        }
        else
        {
          this.$Message.error({
            content:"删除失败",
            duration:2
          });
        }
      }).catch(()=>{
        msg();
        this.$Message.error({
          content:"删除失败",
          duration:2
        });
      });
    },
    copy_success:function()
    {
      this.$Message.success({
        content:"复制成功",
        duration:2
      });
      this.secret_modal=false;
    },
    copy_error:function()
    {
      this.$Message.error({
        content:"复制失败",
        duration:2
      });
    },
    loadFile:function(item)
    {
      let reader  = new FileReader();
      reader.onloadend = ()=>{
        item.text = reader.result;
        item.loaded = true;
      }
      reader.readAsText(item.file);
    },
    preview:function(item){
      item.display = true;
      if(!item.loaded)
        this.loadFile(item)
    },
    preview_cancel:function(item){
      item.display = false;
    }
  }
}
</script>

<style scoped lang="scss">
.normal-font
{
  font-size:1rem;
}
.center
{
  text-align: center;
}
.upload-fun
{
  overflow-y:scroll;
  padding:15px 15px 0 15px;
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
.upload
{
  // margin-bottom:15px;
  height:32px;
  /deep/ span
  {
    font-size:1rem;
  }
}
.button
{
  font-size:1rem;
}
.margin-bottom
{
  margin-bottom:15px;
}
.menu
{
  display:flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
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
.left-spin
{
  text-align:left;
}
.divider
{
  margin-top:12px;
  margin-bottom:12px;
  font-weight:bold;
  // height:2px;
  // background-color:rgba(120, 139, 221, 0.603);
  // background-color:rgb(45, 140, 240);
}
.upload-file-base-info,.detail-info
{
  display:flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  .upload-error
  {
    margin-right:5px;
  }
  .tip
  {
    width:100%;
    margin-right:5px;
  }
  .upload-error
  {
    color:rgb(255, 75, 75);
  }
}
.detail-info
{
  margin-top:4px;
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
.secret
{
  margin-top:4px;
  font-size:0.8rem;
  font-weight:bold;
  font-family: "Tahoma";
  max-height:150px;
  overflow-y:hidden;
  overflow-x:hidden;
  word-break:break-all;
  -webkit-user-select: none;
}
.success
{
  color:#19be6b;
}
.error
{
  color:#ed4014;
}
.error_ex /deep/ input
{
  color:#ed4014;
}
.relative
{
  position:relative;
}
.help
{
  position:absolute;
  top:2px;
  right:4px;
}
</style>