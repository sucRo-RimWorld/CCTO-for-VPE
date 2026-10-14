"""CCTO for VPE release payload, approved art and public copy source contracts."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from build_release import FILES, FOLDER, EXPECTED_WORKSHOP_ID, check_load_folders, check_preview, create_zip, validate


class ReleaseCandidateTests(unittest.TestCase):
    def test_approved_preview_exact_bytes_and_png(self):
        info = json.loads((ROOT / 'Docs/ApprovedPreview.json').read_text())
        orig = (ROOT / info['source']['repository_path']).read_bytes()
        preview = (ROOT / info['preview']['repository_path']).read_bytes()
        self.assertEqual(hashlib.sha256(orig).hexdigest(), info['source']['sha256'])
        self.assertEqual(hashlib.sha256(preview).hexdigest(), info['preview']['sha256'])
        check_preview(preview)
        damaged = bytearray(preview)
        damaged[50] ^= 1
        with self.assertRaises(ValueError):
            check_preview(bytes(damaged))

    def test_exact_distribution_contents_reproducible(self):
        self.assertEqual(len(FILES), 8)
        self.assertEqual((ROOT / 'About/PublishedFileId.txt').read_text().strip(), EXPECTED_WORKSHOP_ID)
        self.assertEqual(set(validate(ROOT)), set(FILES))
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp)/'a.zip', Path(tmp)/'b.zip'
            create_zip(first)
            create_zip(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(set(archive.namelist()), {FOLDER + x for x in FILES})
                self.assertEqual(archive.testzip(), None)
        about = ET.parse(ROOT/'About/About.xml').getroot()
        manifest = ET.parse(ROOT/'About/Manifest.xml').getroot()
        self.assertEqual(about.findtext('modVersion'), manifest.findtext('version'))
        self.assertEqual(about.findtext('name'), 'CCTO for VPE（CCTO VPE対応）')

    def test_conditional_loader_guard_rejects_unreviewed_entries(self):
        check_load_folders((ROOT / 'LoadFolders.xml').read_bytes())
        for bad in (
            b'<loadFolders><v1.6><li>/</li><li>Compatibility/Unknown</li></v1.6></loadFolders>',
            b'<loadFolders><v1.7><li>/</li></v1.7></loadFolders>',
            b'<loadFolders><v1.6><li IfModActive="guessed.id">Compatibility/Unknown</li></v1.6></loadFolders>',
        ):
            with self.assertRaises(ValueError):
                check_load_folders(bad)

    def test_bilingual_public_copy_and_uncertainty(self):
        text = (ROOT/'Docs/SteamWorkshopDescription.txt').read_text(encoding='utf-8')
        two = (ROOT/'Docs/2GameDescription-ja.txt').read_text(encoding='utf-8')
        self.assertLessEqual(len(text.encode('utf-8')), 8000)
        self.assertEqual(text.count('[hr][/hr]'), 1)
        en, ja = text.split('[hr][/hr]')
        for needle in ('20 VPE core plants', 'not been independently tested',
                       'not yet supported', 'new saved classes'):
            self.assertIn(needle.casefold(), en.casefold())
        for needle in ('20種', '実ゲーム未検証', '未対応', '既存セーブ'):
            self.assertIn(needle, ja)
        for heading in ('▼ 特徴','▼ バランス方針','▼ 対応範囲',
                        '▼ 対応・互換性','▼ セーブ互換性','▼ 今後の予定'):
            self.assertIn(heading, two)
        self.assertIn('実ゲーム未検証', two)
        for pack in ('More Plants','Mushrooms','Succulents','Flowers'):
            self.assertIn(pack, text)
        self.assertNotIn('RimWorld 1.7', text)
        self.assertIn('3812412548', text)
        self.assertIn('github.com/sucRo-RimWorld/CCTO-for-VPE/issues', text)

    def test_yada_basenames_filter_development_files(self):
        rules = [s.strip() for s in (ROOT/'.rimignore').read_text().splitlines()
                 if s.strip() and not s.lstrip().startswith('#')]
        self.assertTrue(all('/' not in p and '\\' not in p and not p.startswith('!')
                            for p in rules))
        for excluded in ('Art','Docs','Tests','Scripts','.github','Dist'):
            self.assertIn(excluded, rules)
        self.assertNotIn('LICENSE', rules)


if __name__ == '__main__':
    unittest.main()
