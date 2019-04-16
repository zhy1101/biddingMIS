//信息弹框
function dialog($,type,msg){
   var str = '';	
   var icons = '';
   if(type=='success'){
   	 icons = 'icontishichenggong';
   }else if(type=='error'){
   	 icons = 'iconcaozuoshibai';
   }
   str += '<div class="tip_cont"><div class="tip_icon"><span class="iconfont '+icons+'"></span></div><div class="tip_text">'+msg+'</div></div>'
   $('.dialog-content').show().css("z-index",100);
   $('.dialog-content').html(str);
   $('.dialog-content').fadeOut(3000);
}