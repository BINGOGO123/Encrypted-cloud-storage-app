import Vue from 'vue';
import App from './App.vue';
import VueRouter from 'vue-router';
import ViewUI from "view-design";
import VueClipboard from 'vue-clipboard2'

Vue.use(VueClipboard)
import 'view-design/dist/styles/iview.css';
import preview from 'vue-photo-preview';
import 'vue-photo-preview/dist/skin.css';

import Account from "./account/Account.vue";
import Login from "./account/components/Login.vue";
import Register from "./account/components/Register.vue";
import DataOwner from "./account/components/DataOwner.vue"
import DataOwnerFun from "./appfun/DataOwnerFun.vue";
import DataUserFun from "./appfun/DataUserFun.vue";
import UploadFun from "./appfun/UploadFun.vue";
import User from "./appfun/User.vue";
import UserInformation from "./appfun/UserInformation.vue";
import Search from "./appfun/Search.vue";
import Http404 from "./Http404/Http404.vue";

Vue.use(ViewUI);
Vue.use(VueRouter);
Vue.use(preview);

Vue.config.productionTip = false

const routes = [
  {
    path:"/account",
    component:Account,
    children:[
      {
        path:"login",
        component:Login,
        name:"login"
      },
      {
        path:"register",
        component:Register,
        name:"register"
      },
      {
        path:"dataowner",
        component:DataOwner,
        name:"dataowner"
      },
      {
        path:"",
        redirect:"login"
      }
    ]
  },
  {
    path:"/dataownerfun",
    component:DataOwnerFun,
    children:[
      {
        path:"upload_fun",
        name:"upload_fun",
        component:UploadFun
      },
      {
        path:"user",
        name:"user",
        component:User
      },
      {
        path:"user_information",
        name:"user_information",
        component:UserInformation,
        props:{
          title:"数据所有者",
          attribute:false
        }
      },
      {
        path:"search",
        name:"search",
        component:Search
      },
      {
        path:"",
        redirect:"upload_fun"
      }
    ]
  },
  {
    path:"/datauserfun",
    component:DataUserFun,
    children:[
      {
        path:"user_information",
        name:"user_user_information",
        component:UserInformation,
        props:{
          title:"数据使用者",
          attribute:true
        }
      },
      {
        path:"search",
        name:"user_search",
        component:Search
      },
      {
        path:"",
        redirect:"search"
      }
    ]
  },
  {
    path:"",
    redirect:{name:"login"},
  },
  {
    path:"*",
    component:Http404
  }
];

const router = new VueRouter({routes});

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
