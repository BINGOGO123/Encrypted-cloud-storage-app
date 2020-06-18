<template>
  <div class="http-404">
    <div class="card">
      这不是你该来的地方...
      <br />
      <router-link :to="{name:'login'}">我选择离开</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name:"Http404"
}
</script>

<style scoped>
.http-404
{
  padding:15px 15px 0 15px;
  background-color:#f5f5f5;
  height:100%;
  overflow-x:hidden;
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
</style>