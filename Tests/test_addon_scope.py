"""Ensure the future optional VPE family remains candidates, not falsely shipped."""
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OptionalAddonScopeContract(unittest.TestCase):
    def test_candidate_inventory_is_not_shipped_support(self):
        doc = json.loads((ROOT / "Docs" / "AddonInventory.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["schema_version"], 1)
        self.assertEqual(doc["owner"], "sucRo-RimWorld/CCTO-for-VPE")
        self.assertEqual(doc["state"], "candidate_inventory_not_supported")
        entries = doc["provider_addons"]
        self.assertEqual(
            {x["slug"] for x in entries},
            {"more-plants", "mushrooms", "succulents", "flowers"},
        )
        self.assertEqual(len(entries), len({x["slug"] for x in entries}))
        for item in entries:
            self.assertEqual(item["status"], "candidate_not_implemented")
            self.assertIsNone(item["patch"])
            self.assertIsNone(item["package_id"])
            self.assertEqual(item["source_target_version"], "1.6")
            self.assertRegex(item["inspected_main_commit"], r"^[0-9a-f]{40}$")
            self.assertTrue(item["github_repository"].startswith("Vanilla-Expanded/"))
            self.assertTrue(item["source_notes"])
        self.assertFalse((ROOT / "Patches" / "Addons").exists(),
                         "Inventoried-only addons must not ship unreviewed patches")

    def test_child_packs_not_hard_dependencies(self):
        root = ET.parse(ROOT / "About" / "About.xml").getroot()
        hard_deps = {x.findtext("packageId") for x in root.findall("./modDependencies/li")}
        self.assertEqual(
            hard_deps,
            {"sucro.cropcoldtoleranceoverhaul", "VanillaExpanded.VPlantsE"},
        )
        current = json.loads((ROOT / "Docs" / "PlantBalance.json").read_text())
        self.assertEqual(len(current["include"]), 20)
        self.assertEqual(len(current["exclude"]), 0)


if __name__ == "__main__":
    unittest.main()
