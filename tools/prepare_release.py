#!/usr/bin/env python3
"""Prepare a signed APK and metadata for automatic publication to GitHub Releases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

REPOSITORY = 'MarkOfTheDevil/spk-schedule'
ORIGIN = 'https://github.com/' + REPOSITORY
CERT = 'a4b8cbecd5364c991ea1a286ab7cdd342136f8a77597a52e94c9e97a6c76805d'
PACKAGE = 'ru.spk.schedule'
VERSION = r'[0-9]+(?:\.[0-9]+){1,3}(?:[-+][A-Za-z0-9.-]+)?'
MAX_APK = 100 * 1024 * 1024

def output(*args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True).stdout

def apk_metadata(apk, build_tools, notes):
    certs = output(build_tools / 'apksigner', 'verify', '--print-certs', apk)
    actual = re.findall(r'Signer #\d+ certificate SHA-256 digest: ([a-f0-9]+)', certs)
    if actual != [CERT]:
        raise ValueError('APK must have the original SPK signing certificate.')
    badging = output(build_tools / 'aapt2', 'dump', 'badging', apk)
    package = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
    sdk = re.search(r"(?:minSdkVersion|sdkVersion):'(\d+)'", badging)
    if not package or package[1] != PACKAGE or not sdk:
        raise ValueError('Unexpected package or missing Android version.')
    version, code = package[3], int(package[2])
    if not re.fullmatch(VERSION, version) or len(version) > 40 or not 0 < code <= 2147483647:
        raise ValueError('Invalid application version.')
    if not isinstance(notes, str) or len(notes) > 3000 or not 26 <= int(sdk[1]) <= 1000:
        raise ValueError('Invalid notes or minimum Android version.')
    data = apk.read_bytes()
    if not 0 < len(data) <= MAX_APK:
        raise ValueError('APK size is outside updater limits.')
    name = 'SPK-Raspisanie-' + version + '.apk'
    return dict(schemaVersion=1, packageName=PACKAGE, versionCode=code,
                versionName=version, minSdk=int(sdk[1]), sizeBytes=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                apkUrl=ORIGIN + '/releases/download/v' + version + '/' + name,
                notes=notes)

def verify_release(directory, build_tools):
    manifest = directory / 'latest.json'
    if manifest.is_symlink():
        raise ValueError('Release metadata must be a regular file.')
    data = manifest.read_bytes()
    if len(data) > 32768:
        raise ValueError('Release metadata is too large.')
    meta = json.loads(data)
    version = meta.get('versionName', '')
    if not isinstance(version, str) or not re.fullmatch(VERSION, version):
        raise ValueError('Invalid release version.')
    apk = directory / ('SPK-Raspisanie-' + version + '.apk')
    if apk.is_symlink() or not apk.is_file():
        raise ValueError('Missing regular APK file.')
    actual = apk_metadata(apk, build_tools, meta.get('notes', ''))
    # Compare JSON types as well: True must not be accepted as integer 1.
    if json.dumps(meta, sort_keys=True) != json.dumps(actual, sort_keys=True):
        raise ValueError('Metadata differs from the signed APK.')
    if (directory / 'SHA256SUMS.txt').read_text() != actual['sha256'] + '  ' + apk.name + '\n':
        raise ValueError('Checksum file differs from the APK.')
    return actual, apk

def prepare(apk, directory, build_tools, notes):
    meta = apk_metadata(apk, build_tools, notes)
    previous = directory / 'latest.json'
    if previous.exists():
        old = json.loads(previous.read_text())
        if meta['versionCode'] <= old['versionCode'] and meta != old:
            raise ValueError('Increase versionCode and versionName; never replace an existing version.')
        if meta['versionName'] == old['versionName'] and meta['sha256'] != old['sha256']:
            raise ValueError('This version already contains another APK.')
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / ('SPK-Raspisanie-' + meta['versionName'] + '.apk')
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != meta['sha256']:
        raise ValueError('An APK with the same filename already exists.')
    if apk.resolve() != dest.resolve():
        shutil.copyfile(apk, dest)
    (directory / 'latest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    (directory / 'SHA256SUMS.txt').write_text(meta['sha256'] + '  ' + dest.name + '\n')
    (directory / 'NOTES.md').write_text(notes.strip() + '\n')
    return meta

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path)
    parser.add_argument('--out', type=Path, default=Path('release'))
    parser.add_argument('--notes-file', type=Path)
    parser.add_argument('--verify', action='store_true')
    sdk = Path(os.environ.get('ANDROID_HOME', os.environ.get('ANDROID_SDK_ROOT', '')))
    parser.add_argument('--build-tools', type=Path, default=sdk / 'build-tools/35.0.0')
    args = parser.parse_args()
    if args.verify:
        meta, _ = verify_release(args.out, args.build_tools)
    else:
        if not args.apk or not args.notes_file:
            parser.error('--apk and --notes-file are required to prepare a release')
        meta = prepare(args.apk, args.out, args.build_tools, args.notes_file.read_text())
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
