"""CCTO for VPE engineering-values static regression; not native RimWorld validation."""
import hashlib
import importlib.util
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"Docs/PlantBalance.json").read_text())
SPECCHECK=importlib.util.spec_from_file_location("vpe_patch",ROOT/"Scripts/build_vpe_patch.py")
BUILD=importlib.util.module_from_spec(SPECCHECK)
SPECCHECK.loader.exec_module(BUILD)

class V1BalanceTest(unittest.TestCase):
    def test_reviewed_audit_gate(self):
        audit=json.loads((ROOT/"Docs/Research/ImplementationDecision.json").read_text())
        self.assertEqual(audit["schema_version"],1)
        self.assertEqual(audit["owner"],"sucRo-RimWorld/CCTO-for-VPE")
        self.assertEqual(audit["status"],"ready")
        self.assertEqual(audit["unresolved"],[])
        self.assertEqual(audit["decision"]["kind"],"optional_compatibility")
        self.assertEqual(audit["decision"]["specification"],"Docs/Design.md")
        self.assertTrue({"vanilla_mo","amj","ve","non_ve"}<=set(audit["search"]["ecosystems"]))
        self.assertTrue({"vanilla_mo","amj","ve","non_ve"}<={x["ecosystem"] for x in audit["candidates"]})
        for ev in audit["evidence"]:
            p=(ROOT/ev["path"]).resolve()
            self.assertTrue(p.is_relative_to(ROOT))
            self.assertTrue(p.is_file())
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),ev["sha256"])
        for candidate in audit["candidates"]:
            for key in ("function","historical_fit","dependencies","retention","progression_balance","reuse","maintenance_license"):
                self.assertTrue(candidate["comparison"][key])

    def test_v1_xml_matches_owned_values(self):
        self.assertEqual(DATA["status"],"approved")
        root=ET.parse(ROOT/"Patches/ColdTolerance.xml").getroot()
        ops=root.findall("./Operation/operations/li")
        self.assertEqual(len(ops),28)
        self.assertEqual([x.get("Class") for x in ops].count("PatchOperationConditional"),14)
        self.assertEqual([x.get("Class") for x in ops].count("PatchOperationAddModExtension"),14)
        for species in DATA["include"]:
            row=DATA["plants"][species]
            base=f'/Defs/ThingDef[defName="{species}"]'
            self.assertIs(type(row["cold_dormancy"]),bool)
            self.assertIsInstance(row["growth_min_c"],(int,float))
            self.assertTrue(row["source"] and not row["source"].startswith("pending"))
            self.assertTrue(row["cold_dormancy"] or row["cold_death_c"] is not None)
            if row["cold_death_c"] is not None:
                self.assertLess(row["cold_death_c"],row["growth_min_c"])
            a=[x for x in ops if x.get("Class")=="PatchOperationConditional" and x.findtext("xpath")==base+"/plant/minGrowthTemperature"]
            e=[x for x in ops if x.get("Class")=="PatchOperationAddModExtension" and x.findtext("xpath")==base]
            self.assertEqual((len(a),len(e)),(1,1))
            li=e[0].find("./value/li")
            self.assertEqual(li.get("Class"),"CropColdToleranceOverhaul.ColdToleranceExtension")
            self.assertEqual(li.findtext("coldDeathTemperature"),None if row["cold_death_c"] is None else str(row["cold_death_c"]))
            self.assertEqual(li.findtext("coldDormancy"),"true" if row["cold_dormancy"] else None)
        rendered=ET.tostring(root,encoding="unicode")
        for species in DATA["exclude"]:
            self.assertNotIn(species,rendered)
        for field in ("thingClass","harvestYield","growDays","fertility","DankPyon_"):
            self.assertNotIn(field,rendered)

    def test_generated_xml_is_semantically_current(self):
        expected=BUILD.make_patch(DATA)
        actual=ET.parse(ROOT/"Patches/ColdTolerance.xml").getroot()
        self.assertEqual(ET.canonicalize(ET.tostring(expected,encoding="unicode"),strip_text=True),
                         ET.canonicalize(ET.tostring(actual,encoding="unicode"),strip_text=True))

    def test_invalid_numbers_fail_generator(self):
        bad=json.loads(json.dumps(DATA))
        bad["status"]="pending_balance"
        with self.assertRaises(ValueError):
            BUILD.make_patch(bad)
        bad=json.loads(json.dumps(DATA))
        bad["plants"]["VCE_Tomato"]["growth_min_c"]=None
        with self.assertRaises(ValueError):
            BUILD.make_patch(bad)
        bad=json.loads(json.dumps(DATA))
        bad["plants"]["VCE_Tomato"]["cold_death_c"]=20
        with self.assertRaises(ValueError):
            BUILD.make_patch(bad)

if __name__=="__main__":
    unittest.main()
