"""Compare the seven overlapping VPE plant cold rules to live CCTO source XML.

Run in CI with CCTO_SOURCE_ROOT=.ccto-base and CCTO_PARITY_REQUIRED=1.
This is source equality, not proof of RimWorld's loaded Def or cold behavior.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("CCTO_SOURCE_ROOT", ".ccto-base"))
if not SOURCE.is_absolute():
    SOURCE = ROOT / SOURCE

# (CCTO source file, CCTO ThingDef, VPE ThingDef).
# No other plant is asserted to be a shared CCTO species in VPE v1.
MATCHES = (
    ("Vanilla_ColdTolerance.xml", "Plant_Grass", "VCE_Grass"),
    ("Vanilla_ColdTolerance.xml", "Plant_TallGrass", "VCE_TallGrass"),
    ("Vanilla_ColdTolerance.xml", "Plant_Agave", "VCE_Agave"),
    ("MedievalOverhaul_ColdTolerance.xml", "DankPyon_Plant_Onions", "VCE_Onion"),
    ("MedievalOverhaul_ColdTolerance.xml", "DankPyon_Plant_Pumpkins", "VCE_Pumpkin"),
    ("MedievalOverhaul_ColdTolerance.xml", "DankPyon_Plant_Tomatoes", "VCE_Tomato"),
    ("MedievalOverhaul_ColdTolerance.xml", "DankPyon_Tree_Apple", "VCE_AppleTree"),
)


def values_for(root: ET.Element, def_name: str) -> tuple[int, int | None, bool]:
    """Extract one growth minimum + one CCTO extension by exact ThingDef XPath."""
    xpath = f'/Defs/ThingDef[defName="{def_name}"]'
    growth = [
        item for item in root.iter()
        if item.get("Class") == "PatchOperationConditional"
        and item.findtext("xpath") == xpath + "/plant/minGrowthTemperature"
    ]
    extensions = [
        item for item in root.iter()
        if item.get("Class") == "PatchOperationAddModExtension"
        and item.findtext("xpath") == xpath
    ]
    if len(growth) != 1 or len(extensions) != 1:
        raise AssertionError(
            f"{def_name}: expected 1 growth conditional and 1 CCTO extension; "
            f"found {len(growth)} growth and {len(extensions)} extensions"
        )
    match = growth[0].findtext("./match/value/minGrowthTemperature")
    no_match = growth[0].findtext("./nomatch/value/minGrowthTemperature")
    if match is None or no_match is None or match != no_match:
        raise AssertionError(
            f"{def_name}: inconsistent or missing replace/add growth values: "
            f"{match!r} / {no_match!r}"
        )
    li = extensions[0].find("./value/li")
    if li is None or li.get("Class") != "CropColdToleranceOverhaul.ColdToleranceExtension":
        raise AssertionError(f"{def_name}: wrong/missing CCTO extension class")
    dead_text = li.findtext("coldDeathTemperature")
    dorm_text = li.findtext("coldDormancy")
    if dorm_text not in (None, "true", "false"):
        raise AssertionError(f"{def_name}: invalid coldDormancy: {dorm_text}")
    if dead_text is None and dorm_text != "true":
        raise AssertionError(f"{def_name}: missing cold-death/dormancy behavior")
    return int(match), int(dead_text) if dead_text is not None else None, dorm_text == "true"


def assert_parity(
    addon_xml: ET.Element, ccto_sources: dict[str, ET.Element], balance: dict
) -> None:
    assert len(MATCHES) == len({vpe for _, _, vpe in MATCHES}) == 7
    for ccto_file, ccto_def, vpe_def in MATCHES:
        if vpe_def not in balance["include"]:
            raise AssertionError(f"{vpe_def}: absent from approved VPE scope")
        current = values_for(addon_xml, vpe_def)
        existing = values_for(ccto_sources[ccto_file], ccto_def)
        row = balance["plants"][vpe_def]
        expected = (row["growth_min_c"], row["cold_death_c"], row["cold_dormancy"])
        if current != expected:
            raise AssertionError(
                f"{vpe_def}: committed addon XML {current} != PlantBalance.json {expected}"
            )
        if current != existing:
            raise AssertionError(
                f"{vpe_def} != {ccto_def} in {ccto_file}: "
                f"VPE {current}, CCTO {existing}"
            )


class CctoSharedPlantParityTests(unittest.TestCase):
    def test_seven_shared_species_match_current_ccto_main(self):
        required = os.getenv("CCTO_PARITY_REQUIRED") == "1"
        files = {filename for filename, _, _ in MATCHES}
        missing = sorted(
            filename for filename in files
            if not (SOURCE / "Patches" / filename).is_file()
        )
        if missing:
            if required:
                self.fail(
                    "CCTO_PARITY_REQUIRED=1: actual CCTO source XML is missing: "
                    + ", ".join(missing) + f"; CCTO_SOURCE_ROOT={SOURCE}"
                )
            self.skipTest(
                "Local CCTO source not supplied; set CCTO_SOURCE_ROOT to test "
                "against CCTO main (CI always requires the checkout)"
            )
        upstream = {
            filename: ET.parse(SOURCE / "Patches" / filename).getroot()
            for filename in files
        }
        addon = ET.parse(ROOT / "Patches" / "ColdTolerance.xml").getroot()
        balance = json.loads((ROOT / "Docs" / "PlantBalance.json").read_text())
        assert_parity(addon, upstream, balance)

    def test_parity_checker_rejects_value_drift(self):
        """A changed source value must fail, even if the VPE JSON is unchanged."""
        balance = json.loads((ROOT / "Docs" / "PlantBalance.json").read_text())
        addon = ET.parse(ROOT / "Patches" / "ColdTolerance.xml").getroot()
        onion = values_for(addon, "VCE_Onion")
        self.assertEqual(onion, (5, -3, False))
        mutated = copy.deepcopy(addon)
        for item in mutated.iter():
            if (
                item.get("Class") == "PatchOperationConditional"
                and item.findtext("xpath")
                == '/Defs/ThingDef[defName="VCE_Onion"]/plant/minGrowthTemperature'
            ):
                item.find("./match/value/minGrowthTemperature").text = "6"
                item.find("./nomatch/value/minGrowthTemperature").text = "6"
                break
        else:
            self.fail("VCE_Onion growth patch missing in production XML")
        with self.assertRaisesRegex(AssertionError, "VCE_Onion"):
            values_changed = values_for(mutated, "VCE_Onion")
            if values_changed == onion:
                raise AssertionError("VCE_Onion: mutation was not detected")
            expected = balance["plants"]["VCE_Onion"]["growth_min_c"]
            if values_changed[0] != expected:
                raise AssertionError("VCE_Onion: changed value differs from canonical balance")
