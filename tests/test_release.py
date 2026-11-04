import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import prepare_release as release
import publish_release as publisher

class ReleaseTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.apk = self.root / 'input.apk'
        self.apk.write_bytes(b'unit test apk bytes')
        self.tools = Path('/fake/android/build-tools')

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *args):
        if Path(args[0]).name == 'apksigner':
            return 'Signer #1 certificate SHA-256 digest: ' + release.CERT
        return "package: name='ru.spk.schedule' versionCode='16' versionName='1.11.0'\nminSdkVersion:'26'"

    def prepare(self):
        with patch.object(release, 'output', self.command):
            return release.prepare(self.apk, self.root / 'release', self.tools, 'Исправления')

    def test_prepared_metadata_matches_binary_and_identity(self):
        meta = self.prepare()
        with patch.object(release, 'output', self.command):
            verified, apk = release.verify_release(self.root / 'release', self.tools)
        self.assertEqual(verified, meta)
        self.assertEqual(apk.read_bytes(), self.apk.read_bytes())
        self.assertEqual(meta['sha256'], hashlib.sha256(apk.read_bytes()).hexdigest())
        self.assertIn('/releases/download/v1.11.0/SPK-Raspisanie-1.11.0.apk', meta['apkUrl'])

    def test_wrong_certificate_rejected(self):
        with patch.object(release, 'output', return_value='Signer #1 certificate SHA-256 digest: aabb'):
            with self.assertRaises(ValueError):
                release.apk_metadata(self.apk, self.tools, '')

    def test_manifest_tampering_rejected(self):
        for field, value in [('versionCode', 17), ('schemaVersion', True), ('apkUrl', 'https://evil.test/file.apk'), ('sizeBytes', 0), ('sha256', '0' * 64)]:
            meta = self.prepare()
            meta[field] = value
            (self.root / 'release/latest.json').write_text(json.dumps(meta))
            with patch.object(release, 'output', self.command):
                with self.assertRaises(ValueError):
                    release.verify_release(self.root / 'release', self.tools)
            (self.root / 'release/latest.json').unlink()

    def test_published_version_cannot_be_replaced(self):
        self.prepare()
        self.apk.write_bytes(b'changed apk')
        with patch.object(release, 'output', self.command):
            with self.assertRaises(ValueError):
                release.prepare(self.apk, self.root / 'release', self.tools, 'Исправления')

    def test_draft_is_uploaded_before_publishing(self):
        meta = self.prepare()
        calls = []
        with patch.object(release, 'output', self.command), patch.object(publisher, 'release_view', return_value=None), patch.object(publisher, 'gh', side_effect=lambda *args, **kw: calls.append(args)):
            publisher.publish(self.root / 'release', self.tools, 'abc123', latest=True)
        self.assertEqual([c[1] for c in calls], ['create', 'upload', 'edit'])
        self.assertIn('--draft', calls[0])
        self.assertIn('--draft=false', calls[-1])
        self.assertIn('--latest=true', calls[-1])

    def test_existing_published_version_not_overwritten(self):
        meta = self.prepare()
        calls = []
        with patch.object(release, 'output', self.command), patch.object(publisher, 'release_view', return_value={'isDraft': False}), patch.object(publisher, 'published_manifest', return_value=meta), patch.object(publisher, 'gh', side_effect=lambda *args, **kw: calls.append(args)):
            publisher.publish(self.root / 'release', self.tools, 'abc123')
        self.assertEqual(calls, [])

    def test_conflicting_published_version_rejected(self):
        self.prepare()
        with patch.object(release, 'output', self.command), patch.object(publisher, 'release_view', return_value={'isDraft': False}), patch.object(publisher, 'published_manifest', return_value={}):
            with self.assertRaises(RuntimeError):
                publisher.publish(self.root / 'release', self.tools, 'abc123')

    def test_lost_publish_response_does_not_reupload_published_assets(self):
        meta = self.prepare()
        state = {'release': None}
        calls = []

        def command(*args, **kwargs):
            calls.append(args)
            if args[1] == 'create':
                state['release'] = {'isDraft': True}
            elif args[1] == 'edit':
                state['release'] = {'isDraft': False}
                raise publisher.GitHubError('HTTP 500: Server Error')

        with patch.object(release, 'output', self.command), patch.object(publisher, 'release_view', side_effect=lambda tag: state['release']), patch.object(publisher, 'published_manifest', return_value=meta), patch.object(publisher, 'gh', side_effect=command), patch.object(publisher.time, 'sleep') as sleep:
            publisher.publish(self.root / 'release', self.tools, 'abc123')
        self.assertEqual([c[1] for c in calls], ['create', 'upload', 'edit'])
        sleep.assert_called_once()

    def test_partial_draft_upload_is_resumed_after_server_error(self):
        self.prepare()
        state = {'release': None, 'uploads': 0}
        calls = []

        def command(*args, **kwargs):
            calls.append(args)
            if args[1] == 'create':
                state['release'] = {'isDraft': True}
            elif args[1] == 'upload':
                state['uploads'] += 1
                if state['uploads'] == 1:
                    raise publisher.GitHubError('HTTP 502: Server Error')

        with patch.object(release, 'output', self.command), patch.object(publisher, 'release_view', side_effect=lambda tag: state['release']), patch.object(publisher, 'gh', side_effect=command), patch.object(publisher.time, 'sleep'):
            publisher.publish(self.root / 'release', self.tools, 'abc123')
        self.assertEqual([c[1] for c in calls], ['create', 'upload', 'upload', 'edit'])

    def test_retry_limit_and_permission_errors(self):
        for message, attempts in [('HTTP 503: Server Error', 4), ('HTTP 403: Forbidden', 1), ('HTTP 422: Validation Failed', 1)]:
            with self.subTest(message=message), patch.object(publisher, 'publish_once', side_effect=publisher.GitHubError(message)) as publish, patch.object(publisher.time, 'sleep') as sleep:
                with self.assertRaises(publisher.GitHubError):
                    publisher.publish(self.root / 'release', self.tools, 'abc123')
                self.assertEqual(publish.call_count, attempts)
                self.assertEqual(sleep.call_count, attempts - 1)

if __name__ == '__main__':
    unittest.main()
