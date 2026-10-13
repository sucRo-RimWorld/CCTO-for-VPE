"""Standalone offline guards. These do not claim a loaded RimWorld test."""
import json
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "Docs" / "PlantBalance.json").read_text(encoding="utf-8"))
INCLUDE = {
    "VCE_Grass", "VCE_TallGrass", "VCE_Agave", "VCE_Onion",
    "VCE_Pumpkin", "VCE_Pepper", "VCE_Tomato", "VCE_AppleTree",
    "VCE_PeachTree", "VCE_PlumTree", "VCE_PearTree",
    "VCE_Opuntia", "VCE_BearBerryBush", "VCE_BananaTree",
}
EXCLUDE = {
    "VCE_Peas", "VCE_Eggplant", "VCE_Cabbage", "VCE_Beet",
    "VCE_CherryTree", "VCE_OrangeTree",
}

class ContractTests(unittest.TestCase):
    def test_exact_scope(self):
        self.assertEqual(DATA["schema_version"], 1)
        self.assertEqual(len(DATA["include"]), 14)
        self.assertEqual(len(DATA["exclude"]), 6)
        self.assertEqual(set(DATA["include"]), INCLUDE)
        self.assertEqual(set(DATA["exclude"]), EXCLUDE)
        self.assertEqual(set(DATA["plants"]), INCLUDE)
        self.assertFalse(INCLUDE & EXCLUDE)

    def test_metadata_dependencies(self):
        root = ET.parse(ROOT / "About" / "About.xml").getroot()
        self.assertEqual(root.findtext("packageId"), "sucro.cctoforvpe")
        deps = {x.findtext("packageId") for x in root.findall("./modDependencies/li")}
        self.assertEqual(deps, {"sucro.cropcoldtoleranceoverhaul", "VanillaExpanded.VPlantsE"})
        self.assertEqual(
            {x.text for x in root.findall("./loadAfter/li")}, deps
        )
        self.assertEqual([x.text for x in root.findall("./supportedVersions/li")], ["1.6"])

    def test_balance_not_prematurely_shipped(self):
        output = ROOT / "Patches" / "ColdTolerance.xml"
        if DATA["status"] != "approved":
            self.assertFalse(output.exists(), "Unapproved temperature patch must not ship")
            for species in INCLUDE:
                row = DATA["plants"][species]
                self.assertTrue(any(row[k] is None for k in
                                    ("growth_min_c", "cold_death_c", "cold_dormancy")))
        else:
            self.assertTrue(output.exists(), "Approved balance requires production XML")
            xml = ET.parse(output).getroot()
            defnames = [node.text for node in xml.findall(".//xpath") if node.text and
                        node.text.endswith("]/plant/minGrowthTemperature")]
            self.assertEqual(len(defnames), 28)  # conditional + matching replace
            for species in INCLUDE:
                self.assertTrue(any(f'defName="{species}"' in x for x in defnames))
            for species in EXCLUDE:
                self.assertNotIn(species, ET.tostring(xml, encoding="unicode"))

    def test_generator_refuses_unapproved_values(self):
        if DATA["status"] == "approved":
            self.skipTest("Negative pre-approval guard only")
        res = subprocess.run(
            [sys.executable, str(ROOT / "Scripts" / "build_vpe_patch.py")],
            cwd=str(ROOT), capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 2, res.stdout + res.stderr)
        self.assertFalse((ROOT / "Patches" / "ColdTolerance.xml").exists())

    def test_no_csharp_or_bundled_assemblies(self):
        forbidden = [x for x in ROOT.rglob("*") if x.is_file() and x.suffix.lower() in
                     {".dll", ".cs", ".csproj"} and ".git" not in x.parts]
        self.assertEqual(forbidden, [])

if __name__ == "__main__":
    unittest.main()
