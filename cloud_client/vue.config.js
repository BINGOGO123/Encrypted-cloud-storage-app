module.exports = {
  // lintOnSave:false,
  // publicPath:"/searchable_encryption_static/",
  publicPath:"./",
  pages:{
    search:{
      entry:"./src/main.js",
      template:"./public/index.html",
      filename:"index.html",
      title:"可搜索机密云存储"
    }
  },
  runtimeCompiler:true
}