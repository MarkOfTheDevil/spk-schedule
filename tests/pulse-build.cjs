'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const read=name=>fs.readFileSync('_site/'+name,'utf8');
const manifest=JSON.parse(read('manifest.webmanifest'));
assert.equal(manifest.name,'Pulse · Расписание');
assert.equal(manifest.id,'./'); assert.equal(manifest.scope,'./'); assert.equal(manifest.start_url,'./');
for(const icon of manifest.icons) assert.ok(fs.existsSync('_site/'+icon.src));
const sw=read('sw.js');
const files=vm.runInNewContext(sw.match(/const FILES=(\[[^;]+\]);/)[1]);
for(const file of files) assert.ok(fs.existsSync('_site/'+(file==='./'?'index.html':file)),'Missing offline asset '+file);
const handlers={}, notifications=[];
const scope='https://example.test/spk-schedule/';
vm.runInNewContext(sw, {URL,URLSearchParams,self:{
  registration:{scope,showNotification(title, options){notifications.push({title,...options});return Promise.resolve();}},
  addEventListener(name,handler){handlers[name]=handler;}
}});
function push(payload) {
  handlers.push({data:{json:()=>payload},waitUntil(){}});
  return notifications.at(-1);
}
const reminder=push({title:'Расписание СПК',body:'Первая пара в 08:30',group:'crk:Д015П',date:'2026-11-26'});
assert.equal(reminder.title,'Pulse · Расписание');
assert.equal(reminder.body,'Первая пара в 08:30');
assert.equal(reminder.badge,'icons/pulse-notification.png');
assert.ok(files.includes(reminder.badge));
const link=new URL(reminder.data.url);
assert.equal(link.origin,'https://example.test');
assert.equal(link.pathname,'/spk-schedule/');
assert.equal(link.searchParams.get('group'),'crk:Д015П');
assert.equal(link.searchParams.get('date'),'2026-11-26');
assert.equal(push({title:'Pulse · Тест Push'}).title,'Pulse · Тест Push');
assert.equal(push({title:'Перенос занятия'}).title,'Pulse · Перенос занятия');
assert.equal(push(null).title,'Pulse · Расписание');
handlers.push({data:{json(){throw Error('plain text');},text:()=> 'Расписание на завтра'},waitUntil(){}});
assert.equal(notifications.at(-1).body,'Расписание на завтра');
for(const name of ['index.html','404.html']) {
  const html=read(name);
  for(const match of html.matchAll(/(?:src|href)="([^"#]+\.(?:js|css|svg|png))"/g)) assert.ok(fs.existsSync('_site/'+match[1]),'Missing page asset '+match[1]);
  assert.ok(html.includes('pulse.js')); assert.ok(!html.includes('src="release-notes.js"'));
}
for(const file of fs.readdirSync('_site').filter(x=>x.endsWith('.js'))) new vm.Script(read(file),{filename:file});
const context={window:{},localStorage:{getItem(){return null;}}};vm.createContext(context);
vm.runInContext(read('palettes.js')+';globalThis.catalog=PALETTES',context);
vm.runInContext(read('appearance.js'),context);
assert.equal(context.catalog.length,48);assert.equal(new Set(context.catalog.map(p=>p.id)).size,48);
for(const p of context.catalog) for(const mode of ['light','dark']) {
  const config=context.window.SpkAppearance.normalize({base:p.id,enabled:true});
  assert.equal(config.base,p.id);
  const tokens=context.window.SpkAppearance.tokens(config,mode);
  assert.ok(tokens.bg&&tokens.panel&&tokens.onLime);
}
const rooms=require('../pages/teacher-tools.js'),a=JSON.parse(read('schedule.json')),b=JSON.parse(read('schedule-crk.json'));
const data={groups:[...a.groups,...b.groups],unassignedEntries:b.unassignedEntries};
for(const campus of ['spk','crk']) for(const week of ['even','odd']) for(let day=0;day<6;day++) {
  const model=rooms.model(data,campus,week,day);assert.ok(model.rooms.length);
  for(const slot of model.slots){const r=rooms.availability(model,slot);assert.equal(r.free.length+r.busy.length+r.unknown.length,model.rooms.length);}
}
assert.ok(read('web-push.js').includes('reminder-repair'));
assert.ok(read('web.js').includes('Не удалось синхронизировать Push'));
assert.ok(read('app.js').includes('Подписка Push обновлена'));
console.log('PASS: JS syntax, PWA assets, 48 palettes / 96 constructor variants, both sources and week parities, preserved push recovery.');
