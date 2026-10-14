"""Offline contracts for the dedicated desktop-Steam tag synchronization job."""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from steamworks_tags import (CONFIRM, NOTE, expected_metadata, receipt_path_ok,
                            run_agent, sync, _receipt_matches)


class WorkshopSteamworksTagTests(unittest.TestCase):
    def make_source(self, parent: Path, item: str = '3819497323',
                    versions: tuple[str, ...] = ('1.6',)) -> Path:
        checkout = parent / 'checkout'
        about = checkout / 'About'
        about.mkdir(parents=True)
        (about / 'PublishedFileId.txt').write_text(item + '\n', encoding='ascii')
        (about / 'About.xml').write_text(
            '<ModMetaData><packageId>sucro.cctoforvpe</packageId>'
            '<supportedVersions>' +
            ''.join('<li>' + version + '</li>' for version in versions) +
            '</supportedVersions></ModMetaData>', encoding='utf-8')
        return checkout

    def test_current_source_tags_and_identity(self):
        self.assertEqual(expected_metadata(ROOT), ('Mod', '1.6'))
        self.assertEqual(CONFIRM, 'TAGS_PRIVATE_ONLY')
        self.assertIn('対応バージョン', NOTE)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wrong = self.make_source(root, '3819486090')
            with self.assertRaisesRegex(ValueError, 'Workshop ID differs'):
                expected_metadata(wrong)

    def test_tags_come_from_about_and_do_not_invent_future_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            checkout = self.make_source(Path(tmp), versions=('1.6', '1.7'))
            self.assertEqual(expected_metadata(checkout), ('Mod', '1.6', '1.7'))

    def test_receipt_never_saved_under_checkout_and_is_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            checkout = self.make_source(parent)
            with self.assertRaisesRegex(ValueError, 'outside the GitHub checkout'):
                receipt_path_ok(checkout / 'receipt.json', checkout)
            target = parent / 'receipt.json'
            target.write_text('{}')
            os.chmod(target, 0o644)
            with self.assertRaisesRegex(ValueError, '0600'):
                receipt_path_ok(target, checkout)
            os.chmod(target, 0o600)
            self.assertEqual(receipt_path_ok(target, checkout), target)

    def test_mock_steamworks_update_and_local_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            checkout = self.make_source(parent)
            agent = parent / 'SteamWorkshopAgent'
            agent.write_text('stub')
            os.chmod(agent, 0o700)
            receipt = parent / 'receipt.json'
            probe = {'ready': True, 'steamUserLoggedOn': True, 'steamAppId': 294100}
            submit = {'success': True, 'publishedFileId': 3819497323,
                      'steamAppId': 294100, 'steamUserLoggedOn': True,
                      'submitResult': 'OK', 'timedOut': False,
                      'userNeedsToAcceptWorkshopLegalAgreement': False,
                      'tags': ['Mod', '1.6']}
            with patch('steamworks_tags.run_agent', side_effect=[probe, submit]) as mock:
                response = sync(checkout, agent, receipt, CONFIRM)
                self.assertIn('SUBMITTED', response)
                self.assertEqual(mock.call_count, 2)
                self.assertEqual(mock.call_args.args[1],
                                 ['set-tags', '3819497323', 'Mod', '1.6',
                                  '--confirm', '--changenote', NOTE])
                self.assertEqual(json.loads(receipt.read_text())['tags'], ['Mod', '1.6'])
                self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
            with patch('steamworks_tags.run_agent') as mock:
                self.assertIn('SKIPPED', sync(checkout, agent, receipt, CONFIRM))
                mock.assert_not_called()

    def test_fail_closed_on_wrong_account_and_ambiguous_submit(self):
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            checkout = self.make_source(parent)
            agent = parent / 'SteamWorkshopAgent'
            agent.write_text('stub')
            os.chmod(agent, 0o700)
            receipt = parent / 'receipt.json'
            with self.assertRaisesRegex(ValueError, 'confirmation'):
                sync(checkout, agent, receipt, 'PRIVATE_ONLY')
            with patch('steamworks_tags.run_agent', return_value={
                'ready': False, 'steamUserLoggedOn': False, 'steamAppId': 294100,
            }) as mock:
                with self.assertRaisesRegex(RuntimeError, 'not authenticated'):
                    sync(checkout, agent, receipt, CONFIRM)
                self.assertEqual(mock.call_count, 1)
                self.assertFalse(receipt.exists())

            with patch('steamworks_tags.run_agent', side_effect=[
                {'ready': True, 'steamUserLoggedOn': True, 'steamAppId': 294100},
                {'success': True, 'publishedFileId': 55555, 'steamAppId': 294100,
                 'steamUserLoggedOn': True, 'submitResult': 'OK',
                 'timedOut': False, 'userNeedsToAcceptWorkshopLegalAgreement': False,
                 'tags': ['Mod', '1.6']}
            ]):
                with self.assertRaisesRegex(RuntimeError, 'unverified'):
                    sync(checkout, agent, receipt, CONFIRM)
            self.assertEqual(json.loads(receipt.read_text())['steamworks_submit_result'], 'PENDING')
            with patch('steamworks_tags.run_agent') as mock:
                with self.assertRaisesRegex(ValueError, 'Prior tag submission'):
                    sync(checkout, agent, receipt, CONFIRM)
                mock.assert_not_called()

    def test_agent_json_envelope_strict(self):
        from subprocess import CompletedProcess
        agent = Path('/opt/steam/SteamWorkshopAgent')
        with patch('steamworks_tags.subprocess.run', return_value=CompletedProcess(
            args=[], returncode=0, stdout='{"status":"ok","data":{"ready":true}}', stderr='')):
            self.assertTrue(run_agent(agent, ['steam-session-probe'])['ready'])
        with patch('steamworks_tags.subprocess.run', return_value=CompletedProcess(
            args=[], returncode=0, stdout='{"status":"error","message":"no Steam"}', stderr='')):
            with self.assertRaisesRegex(RuntimeError, 'non-success'):
                run_agent(agent, ['steam-session-probe'])

    def test_workflow_has_manual_and_automatic_authenticated_tag_jobs(self):
        workflow = (ROOT / '.github/workflows/steam-private.yml').read_text()
        self.assertIn('          - sync_tags_private', workflow)
        self.assertIn("CONFIRMATION\" == 'TAGS_PRIVATE_ONLY'", workflow)
        job = workflow.split('  sync_tags:\n', 1)[1]
        self.assertIn('needs: [preflight, upload_private]', job)
        self.assertIn('needs.upload_private.result == \'success\'', job)
        self.assertIn('runs-on: [self-hosted, windows, steamworks-tag-publisher]', job)
        self.assertIn('environment: steam-workshop-private', job)
        self.assertIn('python Scripts/steamworks_tags.py --sync --confirm TAGS_PRIVATE_ONLY', job)
        self.assertNotIn('workshop_build_item', job)
        self.assertNotIn('set-changenote', job)
        self.assertNotIn('new-mod', job)


if __name__ == '__main__':
    unittest.main()
