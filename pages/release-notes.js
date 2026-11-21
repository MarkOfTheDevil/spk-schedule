/* SPK PWA: one-time release notes, stored per version */
(function(){
'use strict';
const version='3.1.1';
const key='spk.release-notes.seen.'+version;
const notes=[
 ['check','Исправлена работа уведомлений','Подписка Push повторно синхронизируется с сервером при запуске.'],
 ['settings','Восстановление Push','В настройках появилась кнопка «Переподключить Push».'],
 ['calendar','Проверка уведомлений','«Тест Push» сообщает о принятии сообщения службой отправки.']
];
function list(){
 return '<ul class="spk-release-list">'+notes.map(([name,title,description])=>'<li><span class="spk-release-icon" aria-hidden="true">'+icon(name)+'</span><div><strong>'+title+'</strong><small>'+description+'</small></div></li>').join('')+'</ul>';
}
let seen=false;
try{seen=localStorage.getItem(key)==='1';}catch(_){}
if(seen)return;
let observer=null,timer=null,opened=false;
function acknowledge(){
 seen=true;
 try{localStorage.setItem(key,'1');}catch(_){}
}
function stopWatching(){if(observer)observer.disconnect();if(timer)clearTimeout(timer);}
function open(){
 if(seen||opened||document.hidden||document.querySelector('.modal:not([hidden]),dialog[open]'))return;
 const dialog=document.createElement('dialog');
 if(typeof dialog.showModal!=='function'){stopWatching();return;}
 dialog.className='spk-release-dialog';
 dialog.setAttribute('aria-labelledby','spkReleaseTitle');
 dialog.innerHTML='<div class="spk-release-inner"><div class="spk-release-handle" aria-hidden="true"></div><div class="spk-release-heading"><span class="spk-release-mark" aria-hidden="true">'+icon('calendar')+'</span><div><div class="spk-release-version">Версия '+version+'</div><h2 id="spkReleaseTitle">Исправление уведомлений</h2></div></div>'+list()+'<button type="button" class="button-primary spk-release-dismiss" autofocus>Понятно</button></div>';
 document.body.appendChild(dialog);
 const button=dialog.querySelector('.spk-release-dismiss');
 button.addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',()=>{acknowledge();dialog.remove();document.removeEventListener('visibilitychange',open);});
 try{dialog.showModal();opened=true;acknowledge();stopWatching();}catch(_){dialog.remove();}
}
function start(){
 if(seen||opened)return;
 observer=new MutationObserver(()=>{if(!timer)timer=setTimeout(()=>{timer=null;open();},180);});
 observer.observe(document.body,{subtree:true,attributes:true,attributeFilter:['hidden','open']});
 document.addEventListener('visibilitychange',open);
 timer=setTimeout(()=>{timer=null;open();},850);
}
if(document.readyState==='complete')start();else window.addEventListener('load',start,{once:true});
})();
