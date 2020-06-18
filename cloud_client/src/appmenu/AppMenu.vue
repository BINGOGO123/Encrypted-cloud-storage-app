<template>
  <div class="app-menu">
    <MenuItem v-for="(item,index) in menu" :key="index"
    :to="item.to"
    :title="item.title"
    :icon="item.icon"
    :active="index==now"
    class="menu-item"
    ></MenuItem>
  </div>
</template>

<script>
import MenuItem from "./components/MenuItem.vue";

export default {
  name:"AppMenu",
  props:{
    menu:Array,
    now:{
      type:Number,
      default:0
    }
  },
  components:{
    MenuItem
  }
}
</script>

<style scoped lang="scss">
.app-menu
{
  display:flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  cursor:pointer;
  .menu-item
  {
    flex:1;
  }
  background-color:#f1f2f9;
}
</style>