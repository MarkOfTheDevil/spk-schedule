/* SPK 3.1 · teacher tools and six-day calendar */
(function(){
'use strict';
const holidayNames={'02-23':'День защитника Отечества','03-08':'Международный женский день','05-01':'Праздник Весны и Труда','05-09':'День Победы','06-12':'День России','11-04':'День народного единства'};
const moved={'2026-03-09':'Перенос выходного','2026-12-31':'Перенос выходного','2027-05-10':'Перенос выходного','2027-12-31':'Перенос выходного'};
// College-specific confirmed exceptions can be added here; no assumed vacations.
const collegeDays={};
function iso(d){return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-');}
function dayOff(d){
 const key=iso(d);
 if(Object.hasOwn(collegeDays,key))return collegeDays[key]||'';
 if(d.getMonth()===0&&d.getDate()<=8)return d.getDate()===7?'Рождество':'Новогодние праздники';
 return holidayNames[key.slice(5)]||moved[key]||(d.getDay()===0?'Воскресенье':'');
}
function minute(s){const m=/^(\d{1,2}):(\d{2})$/.exec(String(s||''));if(!m||+m[1]>23||+m[2]>59)return null;return +m[1]*60 + +m[2];}
function interval(start,end){const a=minute(start),b=minute(end);return a!==null&&b!==null&&b>a?[a,b]:null;}
function overlap(a,b){return a[0]<b[1]&&b[0]<a[1];}
function roomName(x){const v=String(x||'').trim().toUpperCase().replace(/\s/g,'');return /^\d{2,4}(?:\/[0-9А-ЯA-Z]{1,5})?$/.test(v)?v:'';}
function model(data,campus,week,day){
 const rooms=new Set(),slots=new Map(),events=[];
 function addSlot(n,start,end){if(!interval(start,end))return;const key=start+'|'+end;let s=slots.get(key);if(!s){s={key,start,end,numbers:[]};slots.set(key,s);}if(Number.isInteger(+n)&&+n>0&&!s.numbers.includes(+n))s.numbers.push(+n);}
 function record(l,active){
  const v=l.variants||[];for(const item of v){const r=roomName(item.room);if(r)rooms.add(r);if(active&&r)events.push({room:r,when:interval(l.start,l.end)});}
  if(active)addSlot(l.number,l.start,l.end);
 }
 for(const g of data?.groups||[]){if((g.source||'spk')!==campus)continue;for(const w of ['even','odd'])for(let i=0;i<7;i++)for(const l of g.weeks?.[w]?.[i]||[])record(l,w===week&&i===day);}
 // CRK also contains real entries without group IDs (clubs, school pupils etc.).
 if(campus==='crk')for(const e of data?.unassignedEntries||[]){
  const r=roomName(e.room);if(r)rooms.add(r);
  if(e.week!==week||Number(e.day)!==day)continue;
  const times=String(e.time||'').match(/\d{1,2}:\d{2}/g)||[];
  if(r)events.push({room:r,when:interval(times[0],times[1])});
  addSlot(e.number,times[0],times[1]);
 }
 return {rooms:[...rooms].sort((a,b)=>a.localeCompare(b,'ru',{numeric:true})),slots:[...slots.values()].sort((a,b)=>minute(a.start)-minute(b.start)||minute(a.end)-minute(b.end)),events};
}
function availability(m,slot){
 const when=interval(slot?.start,slot?.end);
 if(!when)return {free:[],busy:[],unknown:m.rooms.slice()};
 const busy=new Set(),unknown=new Set();
 for(const e of m.events){if(!e.when)unknown.add(e.room);else if(overlap(when,e.when))busy.add(e.room);}
 return {free:m.rooms.filter(r=>!busy.has(r)&&!unknown.has(r)),busy:m.rooms.filter(r=>busy.has(r)),unknown:m.rooms.filter(r=>!busy.has(r)&&unknown.has(r))};
}
if(typeof module==='object'&&module.exports){module.exports={dayOff,model,availability,roomName};return;}

const store='spk.favorite-teachers.v1';
let favorites=[];
try{const a=JSON.parse(localStorage.getItem(store)||'[]');if(Array.isArray(a))favorites=a.filter(x=>x&&['spk','crk'].includes(x.campus)&&typeof x.id==='string'&&typeof x.name==='string');}catch(_){}
function favoriteKey(c,id){return JSON.stringify([c,id]);}
function has(c,id){return favorites.some(t=>t.campus===c&&t.id===id);}
function star(c,id,name){
 const active=has(c,id);
 return '<button type="button" class="icon-button spk-teacher-star '+(active?'favorited':'')+'" data-spk-teacher-fav="'+esc(favoriteKey(c,id))+'" data-spk-teacher-name="'+esc(name)+'" aria-pressed="'+active+'" aria-label="'+(active?'Удалить из избранного: ':'Добавить в избранное: ')+esc(name)+'">'+icon('star')+'</button>';
}
function toggle(c,id,name){
 const old=favorites.findIndex(t=>t.campus===c&&t.id===id);
 if(old>=0)favorites.splice(old,1);else favorites.push({campus:c,id,name});
 try{localStorage.setItem(store,JSON.stringify(favorites));}catch(_){toast('Не удалось сохранить преподавателя на устройстве.');}
 if(!$('modal').hidden)renderSmartSearch();else render();
 toast(old>=0?'Преподаватель удалён из избранного':'Преподаватель добавлен в избранное');
}
const roomButton=()=>'<button type="button" class="teacher-search-entry spk-room-entry" data-spk-rooms="open">'+icon('room')+'<span><strong>Свободные кабинеты</strong><small>По дате и времени пары</small></span>'+icon('arrow')+'</button>';
const oldRows=teacherRows;
teacherRows=function(list){
 if(!list.length)return oldRows(list);
 return list.map((t,i)=>((i===0||list[i-1].name[0]!==t.name[0])?'<div class="teacher-letter">'+esc(t.name[0])+'</div>':'')+
 '<div class="group-row spk-teacher-row"><button class="teacher-pick" data-teacher="'+esc(t.id)+'"><span class="group-avatar">'+icon('user')+'</span><span class="teacher-result-text"><strong>'+esc(t.name)+'</strong><small>'+groupCountLabel(t.groupCount)+(t.id===state.teacher?' · выбран сейчас':'')+'</small></span>'+icon('arrow')+'</button>'+star(state.campus,t.id,t.name)+'</div>').join('');
};
const oldTeachers=renderTeachers;
renderTeachers=function(){
 const t=currentTeacher();let html=oldTeachers();
 if(t&&!state.teacherSelecting){
  html=html.replace('<div class="eyebrow">ПРЕПОДАВАТЕЛЬ</div>','<div class="spk-teacher-hero-head"><div class="eyebrow">ПРЕПОДАВАТЕЛЬ</div>'+star(state.campus,t.id,t.name)+'</div>');
  return html.replace('</section>', '</section>'+roomButton());
 }
 return html.replace('<div class="teacher-results-heading">',roomButton()+'<div class="teacher-results-heading">');
};
const oldSearch=renderSmartSearch;
renderSmartSearch=function(){
 oldSearch();if(!state.data||state.chooserPurpose==='reminder')return;
 $('groupList').querySelectorAll('.group-row > button[data-search-id]').forEach(b=>{
  const t=plannerIndex.find(e=>e.id===b.dataset.searchId&&e.kind==='teacher');
  if(!t)return;
  b.parentElement.insertAdjacentHTML('beforeend',star(t.campus,TeacherIndex.key(t.label),t.label));
 });
};
const oldFav=renderFavorites;
renderFavorites=function(){
 let html=oldFav().replace('Группы, которые вам нужны чаще всего.','Группы и преподаватели, которые вам нужны чаще всего.');
 html+='<section class="spk-fav-teachers"><h2>Преподаватели</h2>';
 if(!favorites.length)html+='<p class="planner-note">Нажмите звёздочку рядом с преподавателем, чтобы сохранить его расписание.</p>';
 else html+=favorites.slice().sort((a,b)=>a.name.localeCompare(b.name,'ru')).map(t=>{
  const exists=(state.data?.groups||[]).some(g=>(g.source||'spk')===t.campus&&['even','odd'].some(w=>Object.values(g.weeks?.[w]||{}).some(ls=>ls.some(l=>l.variants.some(v=>TeacherIndex.key(v.teacher)===t.id)))));
  return '<div class="fav-card"><button class="fav-open" data-spk-open-teacher="'+esc(favoriteKey(t.campus,t.id))+'" '+(exists?'':'disabled')+'><strong>'+esc(t.name)+'</strong><small>'+(t.campus==='crk'?'ЦРК':'СПК')+' · '+(exists?'Открыть расписание':'Нет в текущей таблице')+'</small></button>'+star(t.campus,t.id,t.name)+'</div>';
 }).join('');
 return html+'<button class="button-primary" data-spk-find-teacher="1">'+icon('search')+' Найти преподавателя</button></section>';
};
const oldControls=renderDayControls;
renderDayControls=function(){
 const m=monday(selectedDate());
 return oldControls().replace(/<button data-day="([0-6])"[^>]*>/g,(tag,n)=>{
  const off=dayOff(SpkPlanner.add(m,+n));
  return tag.replace('weekend ','').replace('class="day ','class="day '+(off?'spk-day-off ':'')).replace(/aria-label="([^"]*)"/,(_,label)=>'aria-label="'+label+(off?', '+esc(off):'')+'"')+( '');
 });
};
const oldDayHeading=renderDayHeading;
renderDayHeading=function(count){
 const off=dayOff(selectedDate());
 return oldDayHeading(count)+(off?'<aside class="spk-day-off-note"><strong>'+esc(off)+'</strong><span>Выходной по календарю шестидневки. Ниже — шаблон расписания; уточняйте занятия по объявлениям колледжа.</span></aside>':'');
};
const oldCalendar=calendarHtml;
calendarHtml=function(){
 return oldCalendar().replace(/<button [^>]*data-calendar-date="(\d{4}-\d{2}-\d{2})"[^>]*>/g,(tag,date)=>{
  const d=SpkPlanner.date(date),off=d&&dayOff(d);if(!off)return tag;
  return tag.replace('class="calendar-day ','class="calendar-day spk-day-off ').replace(/aria-label="([^"]*)"/,(_,label)=>'aria-label="'+label+', '+esc(off)+'"').replace(/>$/,' title="'+esc(off)+'">');
 }).replace('<div class="calendar-legend">','<p class="spk-calendar-legend"><span>●</span> Выходные и праздники по шестидневке</p><div class="calendar-legend">');
};
let roomCampus='spk',roomDate='',roomSlot='';
function drawRooms(){
 const d=SpkPlanner.date(roomDate);
 const week=d&&currentEven(d)?'even':'odd',day=d?(d.getDay()+6)%7:0;
 const m=model(state.data,roomCampus,week,day),off=d&&dayOff(d),meta=state.data?.sources?.[roomCampus];
 if(!m.slots.some(s=>s.key===roomSlot))roomSlot=m.slots[0]?.key||'';
 const slot=m.slots.find(s=>s.key===roomSlot),a=availability(m,slot);
 const tiles=arr=>'<div class="spk-room-grid">'+arr.map(r=>'<span>'+esc(r)+'</span>').join('')+'</div>';
 const result=!d?'<p class="planner-note">Выберите корректную дату.</p>':off?'<aside class="spk-day-off-note"><strong>'+esc(off)+'</strong><span>Работа колледжа в этот день не подтверждена. Кабинеты не отмечаются свободными.</span></aside>':!slot?'<p class="planner-note">На дату нет известных интервалов пар. Свободные кабинеты определить нельзя.</p>':!m.rooms.length?'<p class="planner-note">В выбранном источнике нет известных кабинетов.</p>':
 '<div class="spk-room-summary"><strong>'+a.free.length+'</strong><span>Без занятий по таблице</span></div>'+(a.free.length?tiles(a.free):'<p class="planner-note">Свободных по таблице кабинетов не найдено.</p>')+'<details class="spk-room-details"><summary>Занятые по таблице · '+a.busy.length+'</summary>'+tiles(a.busy)+'</details>'+(a.unknown.length?'<details class="spk-room-details"><summary>Неопределённое время · '+a.unknown.length+'</summary>'+tiles(a.unknown)+'</details>':'');
 $('plannerContent').innerHTML='<div class="spk-room-filters"><label>Источник<select id="spkRoomCampus"><option value="spk" '+(roomCampus==='spk'?'selected':'')+'>СПК</option><option value="crk" '+(roomCampus==='crk'?'selected':'')+'>ЦРК</option></select></label><label>Дата<input type="date" id="spkRoomDate" value="'+esc(roomDate)+'"></label><label class="spk-room-time">Время пары<select id="spkRoomSlot" '+(!m.slots.length?'disabled':'')+'>'+m.slots.map(s=>'<option value="'+esc(s.key)+'" '+(s.key===roomSlot?'selected':'')+'>'+esc(s.numbers.sort((x,y)=>x-y).join('/')+' пара · '+s.start+'–'+s.end)+'</option>').join('')+'</select></label></div><p class="planner-note">'+(week==='even'?'Чётная':'Нечётная')+' неделя · все группы и подгруппы</p>'+result+'<p class="planner-note">Только кабинеты, встречавшиеся в текущем расписании. Дополнительные брони, замены и помещения вне таблицы не учитываются. '+(meta?.error?'Источник недоступен, используется сохранённая копия. ':!meta?'Нет подтверждения актуальности источника. ':'')+(meta?.fetchedAt?'Таблица: '+esc(timestamp(meta.fetchedAt))+'.':'')+'</p>';
}
function openRooms(){roomCampus=state.campus;roomDate=iso(selectedDate());roomSlot='';showPlanner('Свободные кабинеты','');drawRooms();}
document.addEventListener('click',e=>{
 const b=e.target.closest('button');if(!b||b.disabled)return;
 if(b.dataset.spkRooms==='open')openRooms();
 if(b.dataset.spkTeacherFav){try{const [c,id]=JSON.parse(b.dataset.spkTeacherFav);toggle(c,id,b.dataset.spkTeacherName);}catch(_){}}
 if(b.dataset.spkOpenTeacher){try{const [c,id]=JSON.parse(b.dataset.spkOpenTeacher);activateSearchCampus(c);chooseTeacher(id);}catch(_){}}
 if(b.dataset.spkFindTeacher)openTeacherSearch();
});
document.addEventListener('change',e=>{
 if(e.target.id==='spkRoomCampus'){roomCampus=e.target.value;roomSlot='';drawRooms();}
 if(e.target.id==='spkRoomDate'){roomDate=e.target.value;roomSlot='';drawRooms();}
 if(e.target.id==='spkRoomSlot'){roomSlot=e.target.value;drawRooms();}
});
if(state.data)render();
})();
