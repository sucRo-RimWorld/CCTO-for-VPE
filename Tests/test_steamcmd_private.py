"""Offline publisher security regression tests. Never contact Steam in CI."""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from build_release import create_zip, FILES, FOLDER
from steamcmd_private import (
    APPID, VISIBILITY, check_state_path, load_published_id,
    make_vdf, read_updated_id, run_upload, validate_zip_and_copy, vdf_quote,
)


class SteamCMDPrivateContract(unittest.TestCase):
    def test_private_only_and_keyvalues_escaping(self):
        raw = make_vdf(Path('/tmp/Example'), Path('/tmp/Example/About/Preview.png'),
                       'Safe title', 'First line\nSecond "quoted" line', '0.1.0 - First', '0')
        self.assertIn('"appid" "294100"', raw)
        self.assertIn('"visibility" "2"', raw)
        self.assertNotIn('"visibility" "0"', raw)
        self.assertNotIn('"visibility" "1"', raw)
        self.assertIn(r'First line\nSecond \"quoted\" line', raw)
        self.assertIn('"publishedfileid" "0"', raw)
        self.assertEqual(APPID, '294100')
        self.assertEqual(VISIBILITY, '2')
        with self.assertRaises(ValueError):
            make_vdf(Path('/tmp/Example'), Path('/tmp/Preview.png'), 'x', 'desc', 'note', '-1')
        with self.assertRaises(ValueError):
            vdf_quote('a\x00b')

    def test_workflow_cannot_auto_publish_or_change_visibility(self):
        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text(encoding='utf-8')
        self.assertIn('  workflow_dispatch:', workflow)
        self.assertNotIn('  pull_request:', workflow)
        self.assertNotIn('  push:', workflow)
        self.assertIn('default: preflight', workflow)
        self.assertIn('steamcmd-private-publisher', workflow)
        self.assertIn('environment: steam-workshop-private', workflow)
        self.assertIn('refs/heads/main', workflow)
        self.assertIn('PRIVATE_ONLY', workflow)
        self.assertNotIn('upload_public', workflow)

    def test_workflow_zip_digest_is_relative_to_artifact_root(self):
        """The uploaded sha256.txt must verify after download into Dist/."""
        import hashlib
        import subprocess

        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text(encoding='utf-8')
        producer = workflow.split('      - name: Build exactly six subscriber files', 1)[1].split(
            '      - name: Retain candidate for publisher job and auditing', 1)[0]
        consumer = workflow.split('      - name: Verify candidate artifact digest and reviewed source before invoking SteamCMD', 1)[1].split(
            '      - name: SteamCMD private-only create/update', 1)[0]
        self.assertIn('cd Dist && sha256sum CCTO-for-VPE-0.1.0.zip > sha256.txt', producer)
        self.assertIn('cd Dist', consumer)
        self.assertIn('sha256sum -c sha256.txt', consumer)
        self.assertNotIn('sha256sum Dist/CCTO-for-VPE-0.1.0.zip > Dist/sha256.txt', workflow)

        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp) / 'Dist'
            dist.mkdir()
            archive = dist / 'CCTO-for-VPE-0.1.0.zip'
            archive.write_bytes(b'workshop-zip-test-fixture')
            digest = hashlib.sha256(archive.read_bytes()).hexdigest()
            (dist / 'sha256.txt').write_text(
                f'{digest}  {archive.name}\\n', encoding='utf-8')
            result = subprocess.run(
                ['sha256sum', '-c', 'sha256.txt'], cwd=dist,
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('CCTO-for-VPE-0.1.0.zip: OK', result.stdout)
            archive.write_bytes(b'tampered-zip')
            bad = subprocess.run(
                ['sha256sum', '-c', 'sha256.txt'], cwd=dist,
                capture_output=True, text=True, check=False)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('FAILED', bad.stdout)

    def test_no_unapproved_first_creation_or_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'private-item.json'
            check_state_path(state, ROOT)
            with self.assertRaisesRegex(ValueError, 'explicitly authorized'):
                load_published_id(state, create_new=False)
            self.assertEqual(load_published_id(state, create_new=True), '0')
            state.write_text(json.dumps({'schema_version': 1, 'appid': APPID,
                                         'publishedfileid': '123456789',
                                         'private_verified': False}), encoding='utf-8')
            os.chmod(state, 0o600)
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                load_published_id(state, create_new=True)
            with self.assertRaisesRegex(ValueError, 'confirm'):
                load_published_id(state, create_new=False)
            data = json.loads(state.read_text())
            data['private_verified'] = True
            state.write_text(json.dumps(data), encoding='utf-8')
            self.assertEqual(load_published_id(state, create_new=False), '123456789')
            os.chmod(state, 0o644)
            with self.assertRaisesRegex(ValueError, '0600'):
                check_state_path(state, ROOT)
            with self.assertRaises(ValueError):
                check_state_path(ROOT / 'bad-private-state.json', ROOT)

    def test_published_file_id_is_read_only_after_upload_and_checked(self):
        self.assertEqual(read_updated_id('"workshopitem"\n{\n  "publishedfileid" "123456789"\n}'),
                         '123456789')
        for value in ('0', 'NaN', ''):
            with self.assertRaises(ValueError):
                read_updated_id('"publishedfileid" "' + value + '"')

    def test_zip_matches_exact_owner_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            z = Path(tmp) / 'release.zip'
            create_zip(z)
            with tempfile.TemporaryDirectory() as stage:
                content, preview, title, desc, change = validate_zip_and_copy(z, ROOT, Path(stage))
                self.assertEqual({x.relative_to(content).as_posix() for x in content.rglob('*') if x.is_file()}, set(FILES))
                self.assertEqual(preview, content / 'About/Preview.png')
                self.assertIn('CCTO for VPE', title)
                self.assertIn('20 VPE core plants', desc)
                self.assertTrue(change.startswith('0.1.0 - '))
            evil = Path(tmp) / 'changed.zip'
            with zipfile.ZipFile(z) as source, zipfile.ZipFile(evil, 'w') as output:
                for filename in source.namelist():
                    contents = source.read(filename)
                    if filename == FOLDER + 'About/Changelog.txt':
                        contents += b'\nmodified\n'
                    output.writestr(filename, contents)
            with tempfile.TemporaryDirectory() as stage:
                with self.assertRaisesRegex(ValueError, 'byte-for-byte'):
                    validate_zip_and_copy(evil, ROOT, Path(stage))

    def test_mock_steamcmd_first_private_upload_and_safe_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            z = directory / 'candidate.zip'
            create_zip(z)
            fake = directory / 'fake_steamcmd'
            fake.write_text('''#!/usr/bin/env python3
import pathlib, sys
p = pathlib.Path(sys.argv[sys.argv.index('+workshop_build_item') + 1])
t = p.read_text(encoding='utf-8')
assert '"visibility" "2"' in t
assert '"appid" "294100"' in t
if '"publishedfileid" "0"' in t:
    p.write_text(t.replace('"publishedfileid" "0"', '"publishedfileid" "987654321"'), encoding='utf-8')
''', encoding='utf-8')
            os.chmod(fake, 0o700)
            state = directory / 'publisher-private.json'
            with self.assertRaisesRegex(ValueError, 'approval'):
                run_upload(z, ROOT, state, fake, 'localuser', True, '')
            published = run_upload(z, ROOT, state, fake, 'localuser', True, 'PRIVATE_ONLY')
            self.assertEqual(published, '987654321')
            data = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(data['appid'], '294100')
            self.assertEqual(data['publishedfileid'], '987654321')
            self.assertFalse(data['private_verified'])
            self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)
            with self.assertRaisesRegex(ValueError, 'confirm'):
                run_upload(z, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')
            data['private_verified'] = True
            state.write_text(json.dumps(data), encoding='utf-8')
            published_again = run_upload(z, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')
            self.assertEqual(published_again, published)
            self.assertFalse(json.loads(state.read_text())['private_verified'])


if __name__ == '__main__':
    unittest.main()
