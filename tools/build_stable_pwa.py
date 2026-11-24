"""Reproduce the stable PWA preparation without deployment or network refresh.

Integration patches are copied verbatim from publish-pwa-pages.yml.
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with zipfile.ZipFile(root / 'SPK-iPhone-PWA-GitHub-Pages-3.0.0.zip') as archive:
    archive.extractall('_site')
for name in ('ui-polish.css', 'teacher-tools.js', 'teacher-tools.css', 'release-notes.js', 'release-notes.css'):
    shutil.copyfile(root / 'pages' / name, Path('_site') / name)
subprocess.run([sys.executable, str(root / 'pages/collection-themes.py'), '_site'], check=True)

import json
from pathlib import Path
manifest=json.loads(Path('_site/manifest.webmanifest').read_text(encoding='utf-8'))
assert manifest.get('start_url') == './' and manifest.get('scope') == './', 'PWA must use relative paths'
sync=Path('_site/schedule-sync.js').read_text(encoding='utf-8')
assert "'rasp_crk.xlsx':'schedule.xlsx'" in sync, 'PWA is not adapted to GitHub Pages'
assert 'api/schedule?campus=' not in sync, 'Old Cloudflare API still configured'
# Integrate the verified Supabase push API without touching APK artifacts.
push=Path('_site/web-push.js')
client=push.read_text(encoding='utf-8')
endpoint="https://sibbvczmioxnoffnfdlj.supabase.co/functions/v1/spk-push/"
assert "fetch('api/push/'+name," in client
assert "body:payload?JSON.stringify(payload):undefined" in client
client=client.replace("fetch('api/push/'+name,","fetch('"+endpoint+"'+name,")
owner="""function getOwnerToken(){
 const key='spk.push.owner.v1';
 let token=localStorage.getItem(key);
 if(!token){const bytes=crypto.getRandomValues(new Uint8Array(32));
  token=btoa(String.fromCharCode(...bytes)).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'');
  localStorage.setItem(key,token);}
 return token;
}
"""
client=client.replace(" const b64=s=>", " "+owner+"const b64=s=>")
client=client.replace("body:payload?JSON.stringify(payload):undefined", "body:payload?JSON.stringify({...payload,ownerToken:getOwnerToken()}):undefined")
push.write_text(client,encoding='utf-8')
# Reconnect existing subscriptions after an update and expose a manual repair action.
# The server and its VAPID keys are unchanged.
def patch_once(source, old, new, label):
    assert source.count(old) == 1, label + ': integration anchor changed'
    return source.replace(old, new, 1)
client = patch_once(client,
    "catch(e){reason=e.message;return false;}",
    "catch(e){reason=e.message;try{const r=await navigator.serviceWorker.ready;return Notification.permission==='granted'&&!!(await r.pushManager.getSubscription());}catch(_){return false;}}",
    'preserve subscription while push server is temporarily unavailable')
client = patch_once(client,
    "if(!sub)return;\n  await api('subscribe'",
    "if(!sub)throw Error('Подписка Push потеряна. В настройках нажмите «Переподключить Push».');\n  await api('subscribe'",
    'subscription loss feedback')
client = patch_once(client,
    '<button class="text-button" data-action="reminder-test"',
    '<button class="text-button" data-action="reminder-repair">Переподключить Push</button><button class="text-button" data-action="reminder-test"',
    'push recovery button')
push.write_text(client, encoding='utf-8')
web = Path('_site/web.js')
web_source = web.read_text(encoding='utf-8')
web_source = patch_once(web_source,
    "PwaPush.init().then(enabled=>{state.reminder.enabled=enabled;persist(false);const note=document.querySelector('.pwa-notification-status');if(note)note.textContent=PwaPush.status();}).catch(()=>{});",
    """PwaPush.init().then(async enabled=>{
  state.reminder.enabled=enabled;
  persist(false);
  if(enabled){
   try{await PwaPush.updateIfEnabled({...state.reminder,subgroup:state.subgroupsEnabled?state.reminder.subgroup:0},state.anchorDate,state.anchorEven);}
   catch(e){state.reminderMessage='Не удалось синхронизировать Push: '+e.message;}
  }
  if(state.page==='settings')render();
  const note=document.querySelector('.pwa-notification-status');if(note)note.textContent=PwaPush.status();
 }).catch(e=>{state.reminderMessage='Ошибка проверки Push: '+e.message;if(state.page==='settings')render();});""",
    'reconnect push at app startup')
web.write_text(web_source, encoding='utf-8')
app = Path('_site/app.js')
app_source = app.read_text(encoding='utf-8')
app_source = patch_once(app_source,
    "else if(b.dataset.action==='reminder-test')PwaPush.test().then(()=>toast('Проверочное уведомление отправлено')).catch(e=>toast(e.message,5200));",
    """else if(b.dataset.action==='reminder-repair'){
   if(!state.reminder.group){toast('Сначала выберите группу для уведомлений.');}
   else PwaPush.toggle({enabled:true,group:state.reminder.group,subgroup:state.subgroupsEnabled?state.reminder.subgroup:0,hour:state.reminder.hour,minute:state.reminder.minute,anchorDate:state.anchorDate,anchorEven:state.anchorEven})
    .then(()=>{state.reminder.enabled=true;state.reminderMessage='Подписка Push обновлена. Для проверки нажмите «Тест Push».';persist(false);render();toast(state.reminderMessage);})
    .catch(e=>{state.reminderMessage='Не удалось восстановить Push: '+e.message;render();toast(state.reminderMessage,5200);});
  }
  else if(b.dataset.action==='reminder-test')PwaPush.test().then(result=>toast(result.note||'Тест принят службой Push. Проверьте уведомления устройства.',5200)).catch(e=>toast(e.message,5200));""",
    'repair action and truthful push test status')
app.write_text(app_source,encoding='utf-8')

html=Path('_site/index.html')
text=html.read_text(encoding='utf-8')
assert "connect-src 'self'" in text
assert 'href="web.css"' in text
style_link = '<link rel="stylesheet" href="web.css">'
polish_link = '<link rel="stylesheet" href="ui-polish.css">'
assert style_link in text
text = text.replace(style_link, style_link + chr(10) + '  ' + polish_link, 1)
assert '>РАСПИСАНИЕ <span>СПК</span>' in text
text = text.replace('>РАСПИСАНИЕ <span>СПК</span>', '>Расписание <span>СПК</span>', 1)
assert (chr(92) + 'n  ' + polish_link) not in text
text=text.replace("connect-src 'self'", "connect-src 'self' https://sibbvczmioxnoffnfdlj.supabase.co")
html.write_text(text,encoding='utf-8')
# Remove heading-style selector: modern typography is the only supported style.
obsolete_heading = '<label class="field-label" for="appDesignHeading">Заголовки<select id="appDesignHeading"><option value="dot">Точечные</option><option value="sans">Обычные</option></select></label>'
for filename in ('index.html','404.html'):
    page = Path('_site') / filename
    if not page.exists():
        continue
    content = page.read_text(encoding='utf-8')
    assert content.count(obsolete_heading) == 1, filename + ': heading selector changed'
    content = content.replace(obsolete_heading, '', 1)
    field_wrapper = '<div class="appearance-fields"><label class="field-label" for="appDesignScale">'
    assert field_wrapper in content
    content = content.replace(field_wrapper, '<div class="appearance-fields appearance-text-fields"><label class="field-label" for="appDesignScale">', 1)
    page.write_text(content, encoding='utf-8')
appearance = Path('_site/appearance.js')
appearance_src = appearance.read_text(encoding='utf-8')
replacements = [
    ("$('appDesignHeading').value=draft.heading;", ''),
    ("'appDesignHeading','appDesignCards'", "'appDesignCards'"),
    ("appDesignHeading:'heading',", ''),
    ("appDesignHeading:'Вид заголовка «СПК · Расписание».',", '')
]
for old, new in replacements:
    assert appearance_src.count(old) == 1, 'Appearance selector code changed: ' + old
    appearance_src = appearance_src.replace(old, new, 1)
assert 'appDesignHeading' not in appearance_src
appearance.write_text(appearance_src, encoding='utf-8')
for filename in ('index.html','404.html'):
    page = Path('_site') / filename
    if not page.exists():
        continue
    doc = page.read_text(encoding='utf-8')
    script = '<script src="app.js" defer></script>'
    style = '<link rel="stylesheet" href="web.css">'
    assert doc.count(script) == 1 and doc.count(style) == 1
    doc = doc.replace(script, script + chr(10) + '  <script src="teacher-tools.js" defer></script>' + chr(10) + '  <script src="release-notes.js" defer></script>', 1)
    doc = doc.replace(style, style + chr(10) + '  <link rel="stylesheet" href="teacher-tools.css">' + chr(10) + '  <link rel="stylesheet" href="release-notes.css">', 1)
    # Inline SVG inherits the active palette, including custom design tokens.
    from xml.etree import ElementTree
    logo = Path('pages/spk-brand.svg').read_text(encoding='utf-8').strip()
    assert ElementTree.fromstring(logo).tag.endswith('svg')
    import re
    doc, count = re.subn(r'<div class="brand-icon" aria-hidden="true"><svg[^>]*>.*?</svg></div>', lambda _: '<div class="brand-icon spk-brand-logo" aria-hidden="true">'+logo+'</div>', doc, count=1, flags=re.S)
    assert count == 1, filename + ': brand icon anchor not found'
    page.write_text(doc, encoding='utf-8')
for filename in ('app.js','updates.js'):
    p = Path('_site') / filename
    p.write_text(p.read_text(encoding='utf-8').replace('3.0.0','3.1.1'), encoding='utf-8')
# Cloudflare Web Analytics works on external hosts using the manual beacon.
# Token is a PUBLIC site identifier, provided via GitHub Actions repository variable.
import os, re, hashlib
cf_token = os.environ.get('CF_WEB_ANALYTICS_TOKEN', '').strip()
if cf_token and not re.fullmatch(r'[a-fA-F0-9]{32}', cf_token):
    # Accept the whole HTML snippet copied from Cloudflare as well as a bare token.
    matches = re.findall(r'[0-9A-Fa-f]{32}', cf_token)
    if len(matches) != 1:
        raise ValueError('CF_WEB_ANALYTICS_TOKEN must contain exactly one 32-character Cloudflare site token')
    cf_token = matches[0]
if cf_token:
    index = Path('_site/index.html')
    document = index.read_text(encoding='utf-8')
    script_src = "script-src 'self'"
    connect_src = "connect-src 'self'"
    assert document.count(script_src) == 1
    assert document.count(connect_src) == 1
    assert document.count('</body>') == 1
    document = document.replace(script_src, script_src + ' https://static.cloudflareinsights.com', 1)
    document = document.replace(connect_src, connect_src + ' https://cloudflareinsights.com', 1)
    beacon = '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=' + chr(39) + '{"token":"' + cf_token + '"}' + chr(39) + '></script>'
    document = document.replace('</body>', '  ' + beacon + chr(10) + '</body>', 1)
    index.write_text(document, encoding='utf-8')
    print('Cloudflare Web Analytics: beacon enabled for GitHub Pages')
else:
    print('Cloudflare Web Analytics: disabled until repo variable CF_WEB_ANALYTICS_TOKEN is set')
sw=Path('_site/sw.js')
sw_text=sw.read_text(encoding='utf-8')
assert 'spk-iphone-v3-github-pages-3-0-0' in sw_text
assert 'const FILES=[' in sw_text
# A fixed notification tag caused fresh test pushes to replace older ones silently.
assert "tag:'spk-reminder'," in sw_text
sw_text=sw_text.replace("tag:'spk-reminder',", "tag:'spk-reminder-'+Date.now(),",1)
sw_text=sw_text.replace('const FILES=[', "const FILES=['ui-polish.css','teacher-tools.js','teacher-tools.css','release-notes.js','release-notes.css',",1)
sw_text=sw_text.replace('spk-iphone-v3-github-pages-3-0-0','spk-iphone-v3-github-pages-3-0-0-modern-type-no-heading-1')
asset_fingerprint = hashlib.sha256(b''.join(Path('_site', name).read_bytes() for name in ('index.html', 'teacher-tools.js', 'teacher-tools.css', 'ui-polish.css', 'palettes.js', 'appearance.js', 'web.css', 'release-notes.js', 'release-notes.css', 'web-push.js', 'web.js', 'app.js'))).hexdigest()[:12]
sw_text=sw_text.replace('spk-iphone-v3-github-pages-3-0-0-modern-type-no-heading-1', 'spk-iphone-v3-github-pages-3-0-0-modern-type-no-heading-1-' + asset_fingerprint)
sw_text=sw_text.replace('modern-type-no-heading-1-', 'teacher-tools-3-1-0-')
sw.write_text(sw_text,encoding='utf-8')
