/* Run after python tools/build_pulse.py. Uses an isolated localhost origin. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '../_site');
const mime = {'.js':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.webmanifest':'application/manifest+json','.svg':'image/svg+xml','.png':'image/png'};
const server = http.createServer((req,res) => {
  const name = new URL(req.url,'http://localhost').pathname;
  const file = path.resolve(root, '.'+(name === '/' ? '/index.html' : name));
  if (!file.startsWith(root+path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {res.writeHead(404).end();return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'}); fs.createReadStream(file).pipe(res);
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base = 'http://127.0.0.1:'+server.address().port;
  const browser = await chromium.launch({headless:true,...(process.env.PULSE_BROWSER_CHANNEL?{channel:process.env.PULSE_BROWSER_CHANNEL}:{})});
  const errors=[];
  const context=await browser.newContext({viewport:{width:390,height:844}});
  const page=await context.newPage(); page.on('pageerror',e=>errors.push(e.message));
  page.setDefaultTimeout(10000);
  const click=s=>page.locator(s).click();
  const next=()=>click('#pulseNext');
  const settle=()=>page.waitForTimeout(650);
  try {
    await page.goto(base); await page.locator('.pulse-onboarding[open]').waitFor();
    await page.screenshot({path:'test-results/onboarding.png'});
    await next(); assert.equal(await page.locator('#pulseNext').isDisabled(),true);
    await page.locator('#pulseSearch').fill('несуществующая-группа');
    assert.equal(await page.locator('[name=pulseChoice]').count(),0);
    await page.locator('#pulseSearch').fill('');
    const studentId=await page.locator('[name=pulseChoice]').first().getAttribute('value');
    await page.locator('[name=pulseChoice]').first().check(); await next(); await settle();
    assert.equal(await page.locator('.pulse-intro').count(),1);
    assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('pulse.profile.v2')).id),studentId);
    await page.locator('[data-day="0"]').click(); await settle();
    // Exercise the actual touch-pointer swipe listener, including its direction.
    const swipeTarget=page.locator('.timetable-results');
    await swipeTarget.dispatchEvent('pointerdown',{pointerId:1,pointerType:'touch',isPrimary:true,button:0,clientX:280,clientY:400});
    await swipeTarget.dispatchEvent('pointermove',{pointerId:1,pointerType:'touch',isPrimary:true,clientX:170,clientY:402});
    await swipeTarget.dispatchEvent('pointerup',{pointerId:1,pointerType:'touch',isPrimary:true,clientX:90,clientY:402});
    await settle();
    assert.equal(await page.locator('[data-day="1"]').getAttribute('aria-pressed'),'true');
    await page.locator('[data-day="0"]').click(); await settle();
    await page.screenshot({path:'test-results/student.png',fullPage:true});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await click('.bottom-nav [data-action="choose"]');
    await page.locator('#modal:not([hidden])').waitFor();
    await click('#closeModal'); await settle();
    // Existing tools: favorites, calendar, sharing, search, themes and constructor.
    await page.locator('.hero [data-favorite]').click();
    assert.ok((await page.evaluate(()=>JSON.parse(localStorage.getItem('spk.preferences.v1')).favorites)).includes(studentId));
    await click('[data-action="calendar"]'); await page.locator('#plannerModal:not([hidden])').waitFor();
    assert.ok(await page.locator('[data-calendar-date]').count()>=28);
    await click('#closePlanner'); await settle();
    await click('[data-action="share"]'); await page.locator('#shareModal:not([hidden])').waitFor();
    await click('#closeShare'); await settle();
    await click('#globalSearch'); await page.locator('#groupSearch').fill('101');
    assert.ok(await page.locator('#groupList').innerText());
    await click('#closeModal'); await settle();
    await click('[data-page="settings"]'); await settle();
    await page.locator('summary').filter({hasText:'Оформление'}).click();
    await click('[data-action="appearance-open"]'); await page.locator('#appearanceModal:not([hidden])').waitFor();
    await click('#appDesignCancel'); await settle();
    // Editing and canceling must not mutate a saved profile.
    await click('[data-pulse="profile"]'); await click('[data-role="teacher"]'); await click('[data-wizard="close"]');
    assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('pulse.profile.v2')).role),'student');
    await click('[data-pulse="profile"]'); await click('[data-role="teacher"]'); await next();
    const teacherId=await page.locator('[name=pulseChoice]').first().getAttribute('value');
    await page.locator('[name=pulseChoice]').first().check(); await next(); await click('[data-curator="true"]'); await next();
    await page.locator('[name=pulseChoice]').first().check();
    await click('[data-pulse-campus="crk"]'); await page.locator('[name=pulseChoice]').first().check();
    await next(); await settle();
    const p=await page.evaluate(()=>JSON.parse(localStorage.getItem('pulse.profile.v2')));
    assert.equal(p.campus,'spk'); assert.equal(p.id,teacherId); assert.equal(p.groups.length,2); assert.equal(p.curator,true);
    assert.equal(await page.locator('.pulse-group-chip').count(),2);
    await page.locator('[data-day="0"]').click(); await settle();
    await page.screenshot({path:'test-results/curator.png',fullPage:true});
    await page.locator('.pulse-group-chip').last().click(); await settle();
    assert.equal(await page.evaluate(()=>document.documentElement.dataset.campus),'crk');
    await click('[data-pulse="home"]'); await settle();
    assert.equal(await page.evaluate(()=>document.documentElement.dataset.campus),'spk');
    await page.locator('[data-spk-rooms="open"]').click(); await settle();
    assert.ok((await page.locator('#plannerModal').innerText()).includes('кабинет'));
    await click('#closePlanner'); await settle();
    // Reload restores the personal teacher screen without changing the role.
    await page.reload(); await page.locator('.pulse-intro').waitFor();
    assert.equal(await page.locator('.pulse-onboarding').count(),0);
    assert.equal(await page.locator('.pulse-group-chip').count(),2);
    await click('#themeToggle'); await settle();
    await page.screenshot({path:'test-results/light.png',fullPage:true});
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(()=>document.documentElement.dataset.motion==='off');
    assert.equal(await page.evaluate(()=>document.documentElement.dataset.motion),'off');
    for (const width of [320,768,1440]) {
      await page.setViewportSize({width,height:900});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'horizontal overflow at '+width);
    }
    await page.evaluate(()=>navigator.serviceWorker.ready);
    await page.waitForFunction(()=>!!navigator.serviceWorker.controller);
    await context.setOffline(true); await page.reload(); await page.locator('.pulse-intro').waitFor();
    assert.equal(await page.locator('.pulse-group-chip').count(),2);
    await context.setOffline(false);
    assert.deepEqual(errors,[]);
    // Existing users keep their theme, favorites and constructor while onboarding.
    const legacy=await browser.newContext({viewport:{width:390,height:844}});
    await legacy.addInitScript(({id})=>{
      localStorage.setItem('spk.preferences.v1',JSON.stringify({group:id,campus:'spk',theme:'light',palette:'ocean',favorites:[id],animations:false}));
      localStorage.setItem('spk.appearance.v1',JSON.stringify({enabled:true,base:'ocean',radius:24,colors:{light:{background:'#edf2ff'},dark:{}}}));
    },{id:studentId});
    const oldPage=await legacy.newPage();oldPage.setDefaultTimeout(10000);
    await oldPage.goto(base);await oldPage.locator('.pulse-onboarding[open]').waitFor();
    assert.equal(await oldPage.evaluate(()=>document.documentElement.dataset.theme),'light');
    assert.equal(await oldPage.evaluate(()=>document.documentElement.dataset.customDesign),'on');
    await oldPage.locator('[data-role="teacher"]').click();await oldPage.locator('#pulseNext').click();
    await oldPage.locator('[data-pulse-campus="crk"]').click();await oldPage.locator('[name=pulseChoice]').first().check();
    await oldPage.locator('#pulseNext').click();await oldPage.locator('[data-curator="false"]').click();await oldPage.locator('#pulseNext').click();
    await oldPage.locator('.pulse-intro').waitFor();
    const migrated=await oldPage.evaluate(()=>({profile:JSON.parse(localStorage.getItem('pulse.profile.v2')),old:JSON.parse(localStorage.getItem('spk.preferences.v1'))}));
    assert.equal(migrated.profile.campus,'crk');assert.equal(migrated.profile.curator,false);
    assert.equal(migrated.old.theme,'light');assert.equal(migrated.old.palette,'ocean');assert.deepEqual(migrated.old.favorites,[studentId]);
    await legacy.close();
    console.log('PASS: student, teacher curator, cross-campus groups, cancellation, persistence, favorites, search, calendar, sharing, rooms, theme designer, reduced motion, responsive layout, service worker offline reload.');
  } catch (error) { await page.screenshot({path:'test-results/failure.png',fullPage:true}); console.error('Page errors:',errors); throw error; }
  finally { await browser.close(); server.close(); }
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
