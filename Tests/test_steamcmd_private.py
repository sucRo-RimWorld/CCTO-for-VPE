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
from build_release import create_zip, FILES, FOLDER, EXPECTED_WORKSHOP_ID
from steamcmd_private import (
    APPID, VISIBILITY, check_state_path, load_published_id,
    current_changenote, make_vdf, read_updated_id, run_upload,
    validate_zip_and_copy, vdf_quote, workshop_tags,
)


class SteamCMDPrivateContract(unittest.TestCase):
    def test_current_changenote_includes_body_and_stops_before_old_versions(self):
        changelog = ('# ignored comment\n'
                     '0.2.0 - New compatibility\n'
                     '- English details\n'
                     '- 日本語の詳細\n'
                     '\n'
                     '0.1.0 - Previous release\n'
                     '- old details\n')
        note = current_changenote(changelog, '0.2.0')
        self.assertEqual(note, '0.2.0 - New compatibility\n'
                               '- English details\n- 日本語の詳細')
        self.assertNotIn('Previous release', note)
        self.assertIn('old details', current_changenote(changelog, '0.1.0'))
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            current_changenote(changelog, '0.3.0')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            current_changenote(changelog + '\n0.1.0 - Duplicate\n- more\n', '0.1.0')
        with self.assertRaisesRegex(ValueError, 'no body'):
            current_changenote('0.3.0 - Header only\n', '0.3.0')

    def test_expected_workshop_tags_follow_about_xml(self):
        from xml.etree import ElementTree as ET
        about = ET.fromstring((ROOT / 'About/About.xml').read_bytes())
        expected = [x.text for x in about.findall('./supportedVersions/li')]
        self.assertEqual(workshop_tags(about), ('Mod', *expected))
        fake = ET.fromstring('<ModMetaData><supportedVersions><li>1.6</li>'
                             '<li>1.7</li></supportedVersions></ModMetaData>')
        self.assertEqual(workshop_tags(fake), ('Mod', '1.6', '1.7'))
        for bad in ('<ModMetaData/>',
                    '<ModMetaData><supportedVersions><li>1.6</li>'
                    '<li>1.6</li></supportedVersions></ModMetaData>',
                    '<ModMetaData><supportedVersions><li>garbage</li>'
                    '</supportedVersions></ModMetaData>'):
            with self.assertRaises(ValueError):
                workshop_tags(ET.fromstring(bad))

    def test_selected_workshop_id_is_staged_and_immutable(self):
        self.assertEqual(EXPECTED_WORKSHOP_ID, '3819497323')
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / 'release.zip'
            create_zip(bundle)
            with zipfile.ZipFile(bundle) as archive:
                self.assertEqual(archive.read(FOLDER + 'About/PublishedFileId.txt').strip(),
                                 EXPECTED_WORKSHOP_ID.encode('ascii'))
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'private.json'
            state.write_text(json.dumps({'schema_version': 1, 'appid': APPID,
                                          'publishedfileid': '3819486090',
                                          'private_verified': True}), encoding='utf-8')
            os.chmod(state, 0o600)
            candidate = Path(tmp) / 'candidate.zip'
            create_zip(candidate)
            fake = Path(tmp) / 'steamcmd'
            fake.write_text('#!/bin/sh\nexit 0\n')
            os.chmod(fake, 0o700)
            with self.assertRaisesRegex(ValueError, 'differs from'):
                run_upload(candidate, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')
            with self.assertRaisesRegex(ValueError, 'Creation disabled'):
                run_upload(candidate, ROOT, state, fake, 'localuser', True, 'PRIVATE_ONLY')

    def test_private_only_and_keyvalues_escaping(self):
        raw = make_vdf(Path('/tmp/Example'), Path('/tmp/Example/About/Preview.png'),
                       'Safe title', 'First line\nSecond "quoted" line', '0.1.0 - First', '0')
        self.assertIn('"appid" "294100"', raw)
        self.assertIn('"visibility" "2"', raw)
        self.assertNotIn('"visibility" "0"', raw)
        self.assertNotIn('"visibility" "1"', raw)
        self.assertIn('First line\nSecond ' + r'\"quoted\" line', raw)
        self.assertNotIn(r'First line\nSecond', raw)
        self.assertIn('"publishedfileid" "0"', raw)
        self.assertEqual(APPID, '294100')
        self.assertEqual(VISIBILITY, '2')
        with self.assertRaises(ValueError):
            make_vdf(Path('/tmp/Example'), Path('/tmp/Preview.png'), 'x', 'desc', 'note', '-1')
        with self.assertRaises(ValueError):
            vdf_quote('a\x00b')

    def test_workshop_description_keeps_real_line_breaks(self):
        description = (ROOT / 'Docs/SteamWorkshopDescription.txt').read_text(encoding='utf-8')
        self.assertNotIn(r'\n', description)
        raw = make_vdf(Path('/tmp/Example'), Path('/tmp/Preview.png'),
                       'Safe title', description, '0.1.0 - First', '123456789')
        self.assertIn('"description" "' + description + '"', raw)
        self.assertNotIn(r'\n', raw)
        self.assertEqual(vdf_quote('first\r\nsecond\rthird'), '"first\nsecond\nthird"')
        self.assertIn('"publishedfileid" "123456789"', raw)
        self.assertIn('"visibility" "2"', raw)

    def test_workflow_cannot_auto_publish_or_change_visibility(self):
        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text(encoding='utf-8')
        self.assertIn('  workflow_dispatch:', workflow)
        self.assertNotIn('  pull_request:', workflow)
        self.assertNotIn('  push:', workflow)
        self.assertIn('default: preflight', workflow)
        self.assertIn('Creation disabled', workflow)
        self.assertIn('steamcmd-private-publisher', workflow)
        self.assertIn('environment: steam-workshop-private', workflow)
        self.assertIn('refs/heads/main', workflow)
        self.assertIn('PRIVATE_ONLY', workflow)
        self.assertNotIn('upload_public', workflow)


    def test_publisher_runner_check_is_nonpublishing_and_sha_pinned(self):
        """Only a main SHA-pinned manual dispatch can check the publisher host."""
        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text(encoding='utf-8')
        self.assertIn('          - runner_check', workflow)
        self.assertIn('default: preflight', workflow)
        authorization = workflow.split('      - name: Verify manual default-branch authorization', 1)[1].split(
            '      - uses: actions/checkout@v4', 1)[0]
        self.assertIn('refs/heads/main', authorization)
        self.assertIn('"$EXPECTED_SHA" == "$GITHUB_SHA"', authorization)
        self.assertIn('"$REQUESTED_MODE" == \'runner_check\'', authorization)
        self.assertIn('"$CREATE_NEW" == \'false\'', authorization)
        self.assertIn('-z "$CONFIRMATION"', authorization)
        self.assertIn('exit 2', authorization)

        check = workflow.split('  runner_check:\n', 1)[1].split('  upload_private:\n', 1)[0]
        self.assertIn("if: ${{ inputs.mode == 'runner_check' }}", check)
        self.assertIn('needs: preflight', check)
        self.assertIn('runs-on: [self-hosted, linux, steamcmd-private-publisher]', check)
        self.assertIn('environment: steam-workshop-private', check)
        self.assertIn('uses: actions/checkout@v4', check)
        self.assertIn('persist-credentials: false', check)
        self.assertIn('uses: actions/download-artifact@v4', check)
        self.assertIn('name: ccto-for-vpe-0.1.0-private-candidate', check)
        self.assertIn('path: Dist', check)
        self.assertIn('cd Dist', check)
        self.assertIn('sha256sum -c sha256.txt', check)
        for forbidden in ('steamcmd_private.py', 'workshop_build_item',
                          'CCTO_STEAM_ACCOUNT', 'CCTO_STEAMCMD_BIN',
                          'CCTO_STEAM_STATE', '--execute', 'CREATE_NEW:'):
            self.assertNotIn(forbidden, check)

    def test_workflow_zip_digest_is_relative_to_artifact_root(self):
        """The uploaded sha256.txt must verify after download into Dist/."""
        import hashlib
        import subprocess

        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text(encoding='utf-8')
        producer = workflow.split('      - name: Build exactly seven subscriber files', 1)[1].split(
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
                f'{digest}  {archive.name}' + chr(10), encoding='utf-8')
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
                self.assertEqual((content / 'About/PublishedFileId.txt').read_text().strip(),
                                 EXPECTED_WORKSHOP_ID)
                self.assertIn('CCTO for VPE', title)
                self.assertIn('20 VPE core plants', desc)
                self.assertTrue(change.startswith('0.1.0 - '))
                self.assertIn('- Added growth temperature', change)
                self.assertIn('- 実ゲーム未検証。', change)
                self.assertGreaterEqual(len(change.splitlines()), 4)
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

    def test_mock_steamcmd_updates_existing_private_item_only(self):
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
assert '"publishedfileid" "3819497323"' in t
assert '"publishedfileid" "0"' not in t
''', encoding='utf-8')
            os.chmod(fake, 0o700)
            state = directory / 'publisher-private.json'
            with self.assertRaisesRegex(ValueError, 'approval'):
                run_upload(z, ROOT, state, fake, 'localuser', False, '')
            with self.assertRaisesRegex(ValueError, 'No saved Workshop ID'):
                run_upload(z, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')
            state.write_text(json.dumps({'schema_version': 1, 'appid': APPID,
                                         'publishedfileid': EXPECTED_WORKSHOP_ID,
                                         'private_verified': True}), encoding='utf-8')
            os.chmod(state, 0o600)
            published = run_upload(z, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')
            self.assertEqual(published, EXPECTED_WORKSHOP_ID)
            data = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(data['appid'], '294100')
            self.assertEqual(data['publishedfileid'], EXPECTED_WORKSHOP_ID)
            self.assertFalse(data['private_verified'])
            self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)
            with self.assertRaisesRegex(ValueError, 'confirm'):
                run_upload(z, ROOT, state, fake, 'localuser', False, 'PRIVATE_ONLY')


if __name__ == '__main__':
    unittest.main()
