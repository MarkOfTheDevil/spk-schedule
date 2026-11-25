"""Build Pulse preview from the exact stable PWA preparation; never deploys."""
import hashlib
import json
import re
import runpy
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build():
    # Run from repository root, like the stable workflow. Keep original ZIP immutable.
    import os
    os.chdir(ROOT)
    site = ROOT / '_site'
    if site.exists():
        if site.is_symlink() or site.resolve().parent != ROOT.resolve():
            raise ValueError('Refusing to replace a build directory outside the repository')
        shutil.rmtree(site)
    runpy.run_path(str(ROOT / 'tools/build_stable_pwa.py'))
    for source in (ROOT / 'pulse').iterdir():
        if source.is_file() and source.suffix in ('.js', '.css', '.svg', '.png'):
            shutil.copyfile(source, site / source.name)
    for name in ('index.html', '404.html'):
        path = site / name
        text = path.read_text(encoding='utf-8')
        text = text.replace('<script src="release-notes.js" defer></script>', '<script src="profile.js" defer></script>\n  <script src="pulse.js" defer></script>\n  <script src="brand.js" defer></script>')
        text = text.replace('</head>', '  <link rel="stylesheet" href="pulse.css">\n</head>')
        text = re.sub(r'<title>.*?</title>', '<title>Pulse · Расписание</title>', text)
        text = text.replace('name="apple-mobile-web-app-title" content="Расписание СПК"', 'name="apple-mobile-web-app-title" content="Pulse"')
        text = re.sub(r'<div class="brand-icon spk-brand-logo" aria-hidden="true">.*?</div>', '<div class="brand-icon" aria-hidden="true"><img class="pulse-mark" src="pulse-mark.png" alt=""></div>', text, count=1, flags=re.S)
        text = text.replace('Расписание <span>СПК</span>', 'Pulse <span>2.0</span>')
        text = text.replace('<button data-page="schedule" data-campus="spk" class="nav-item active"><span id="navCalendar"></span><span>СПК</span></button>', '<button data-pulse="home" class="nav-item"><span id="navCalendar"></span><span>Мой день</span></button>')
        text = text.replace('<button data-page="schedule" data-campus="crk" class="nav-item"><span id="navCrk"></span><span>ЦРК</span></button>', '<button data-action="choose" class="nav-item"><span id="navCrk"></span><span>Группы</span></button>')
        text = text.replace('<button data-page="teachers" class="nav-item">', '<button data-action="teachers-choose" class="nav-item">')
        path.write_text(text, encoding='utf-8')
    manifest = json.loads((site / 'manifest.webmanifest').read_text(encoding='utf-8'))
    manifest.update(name='Pulse · Расписание', short_name='Pulse', background_color='#121217', theme_color='#121217')
    (site / 'manifest.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False), encoding='utf-8')
    for name in ('app.js', 'updates.js'):
        path = site / name
        path.write_text(path.read_text(encoding='utf-8').replace('3.1.1', '2.0 preview').replace('<h3>Расписание СПК</h3>', '<h3>Pulse</h3>'), encoding='utf-8')
    for name in ('icon-192.png', 'icon-512.png', 'apple-touch-icon.png'):
        if not (ROOT / 'pulse/icons' / name).is_file():
            raise FileNotFoundError('Missing Pulse launcher icon: '+name)
    for source in (ROOT / 'pulse/icons').glob('*'):
        shutil.copyfile(source, site / 'icons' / source.name)
    sw = (site / 'sw.js').read_text(encoding='utf-8')
    sw = sw.replace('const FILES=[', "const FILES=['pulse.css','pulse.js','profile.js','pulse-mark.png','brand.js',", 1)
    digest = hashlib.sha256(b''.join(p.read_bytes() for p in sorted(site.rglob('*')) if p.is_file() and p.name != 'sw.js')).hexdigest()[:16]
    sw = re.sub(r"const CACHE='[^']+'", "const CACHE='spk-iphone-v3-pulse-2-" + digest + "'", sw)
    (site / 'sw.js').write_text(sw, encoding='utf-8')
    print('Pulse 2.0 preview built in _site. No publication performed.')

if __name__ == '__main__':
    build()
