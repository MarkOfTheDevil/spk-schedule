'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const profile = require('../pulse/profile.js');
test('rejects corrupt, incomplete and future profiles', () => {
  for (const value of [null, [], {}, {version:3,role:'student',id:'1'}, {version:2,role:'student',id:''}]) assert.equal(profile.normalize(value), null);
  assert.equal(profile.read({getItem:()=>'{bad'}), null);
  assert.equal(profile.read({getItem:()=>{throw Error('unavailable');}}), null);
});
test('student strips curator state; teacher retains cross-campus unique group IDs', () => {
  const student=profile.normalize({version:2,role:'student',id:'A',curator:true,groups:['A']});
  assert.deepEqual(student.groups, []); assert.equal(student.curator, false);
  const teacher=profile.normalize({version:2,role:'teacher',id:'T',campus:'spk',curator:true,groups:['A','crk:B','A',null]});
  assert.deepEqual(teacher.groups, ['A','crk:B']);
});
test('save is transactional and does not overwrite existing preferences', () => {
  const values=new Map([['spk.preferences.v1','existing']]);
  const storage={getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)};
  const p={version:2,role:'teacher',campus:'crk',id:'T',curator:false,groups:[]};
  assert.deepEqual(profile.read(storage),null);
  assert.deepEqual(profile.save(storage,p),p);
  assert.deepEqual(profile.read(storage),p);
  assert.equal(values.get('spk.preferences.v1'),'existing');
  assert.throws(()=>profile.save(storage,{...p,curator:true}),/группы/);
  assert.deepEqual(profile.read(storage),p);
  assert.throws(()=>profile.save({setItem:()=>{throw Error('quota');}},p),/quota/);
});
