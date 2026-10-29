#!/usr/bin/env python3
"""Publish verified signed APKs; publish the manifest and APK together, as a draft first."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from prepare_release import REPOSITORY, verify_release

def gh(*args, optional=False):
    result = subprocess.run(['gh', *args, '--repo', REPOSITORY], capture_output=True, text=True)
    if result.returncode:
        if optional and ('release not found' in result.stderr.lower() or 'no releases found' in result.stderr.lower() or 'HTTP 404' in result.stderr):
            return None
        raise RuntimeError(result.stderr.strip() or 'GitHub command failed.')
    return result.stdout

def release_view(tag):
    result = gh('release', 'view', tag, '--json', 'isDraft,tagName', optional=True)
    return json.loads(result) if result is not None else None

def published_manifest(tag):
    with tempfile.TemporaryDirectory() as temp:
        gh('release', 'download', tag, '--pattern', 'latest.json', '--dir', temp)
        return json.loads((Path(temp) / 'latest.json').read_text())

def publish(directory, build_tools, target, latest=False):
    meta, apk = verify_release(directory, build_tools)
    tag = 'v' + meta['versionName']
    existing = release_view(tag)
    if existing and not existing['isDraft']:
        if published_manifest(tag) != meta:
            raise RuntimeError('Published ' + tag + ' differs from local metadata. Increase the version.')
        print(tag + ' is already published; keeping its assets unchanged.')
        if latest:
            gh('release', 'edit', tag, '--latest')
        return
    if existing is None:
        gh('release', 'create', tag, '--target', target, '--title', 'Расписание СПК ' + meta['versionName'],
           '--notes-file', str(directory / 'NOTES.md'), '--draft')
    # A failed run leaves a draft, so phones never see a partial release.
    gh('release', 'upload', tag, str(apk), str(directory / 'latest.json'),
       str(directory / 'SHA256SUMS.txt'), '--clobber')
    gh('release', 'edit', tag, '--draft=false', '--latest=' + str(latest).lower())
    print('Published ' + tag)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-tools', type=Path, required=True)
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    if os.environ.get('GITHUB_REPOSITORY', REPOSITORY) != REPOSITORY:
        raise RuntimeError('This publisher is bound to ' + REPOSITORY)
    current, _ = verify_release(Path('release'), args.build_tools)
    archive = []
    for manifest in Path('release-archive').glob('*/latest.json'):
        metadata, _ = verify_release(manifest.parent, args.build_tools)
        if metadata['versionCode'] >= current['versionCode']:
            raise RuntimeError('Historical release must be older than the current release.')
        archive.append((metadata['versionCode'], manifest.parent))
    # Refuse a stale run that would make an older APK the latest release.
    latest_raw = gh('release', 'view', '--json', 'tagName', optional=True)
    if latest_raw is not None:
        latest = published_manifest(json.loads(latest_raw)['tagName'])
        if latest['versionCode'] > current['versionCode']:
            raise RuntimeError('A newer release is already published; refusing to roll it back.')
    for _, directory in sorted(archive):
        publish(directory, args.build_tools, args.target)
    publish(Path('release'), args.build_tools, args.target, latest=True)

if __name__ == '__main__':
    main()
