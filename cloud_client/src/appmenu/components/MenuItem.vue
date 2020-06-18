<template>
  <div class="menu-item" @click="go" :class="{'active':active}">
    <Icon :type="icon" :size="size"></Icon>
    <div class="title">{{title}}</div>
  </div>
</template>

<script>
export default {
  name:"MenuItem",
  props:{
    to:Object,
    icon:String,
    title:String,
    size:{
      type:Number,
      default:25
    },
    active:{
      type:Boolean,
      default:false
    }
  },
  methods:{
    go:function(){
      if(!this.active)
        this.$router.push(this.to);
    }
  }
}
</script>

<style scoped>
.menu-item
{
  display:flex;
  flex-direction: column;
  align-items:center;
  justify-content: space-around;
  padding-top:5px;
  padding-bottom:5px;
}
.title
{
  font-size:0.9rem;
}
.menu-item.active
{
  /* font-weight:bold; */
  color:#2d8cf0;
}
</style>