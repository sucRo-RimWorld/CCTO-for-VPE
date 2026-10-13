#!/usr/bin/env python3
"""Generate CCTO for VPE production XML only after all 14 values are finalized."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "Docs" / "PlantBalance.json"
OUTPUT = ROOT / "Patches" / "ColdTolerance.xml"

def make_patch(data: dict) -> ET.Element:
    include = data["include"]
    exclude = data["exclude"]
    plants = data["plants"]
    if len(include) != 14 or len(set(include)) != 14 or len(exclude) != 6:
        raise ValueError("VPE v1 requires exactly 14 ordinary plants / 6 custom exclusions")
    if set(plants) != set(include) or set(include) & set(exclude):
        raise ValueError("Inventory is inconsistent")
    if data["status"] != "approved":
        raise ValueError("Balance status is not approved; refuse production XML")
    root = ET.Element("Patch")
    seq = ET.SubElement(root, "Operation", {"Class": "PatchOperationSequence"})
    ops = ET.SubElement(seq, "operations")
    for defname in include:
        value = plants[defname]
        low = value.get("growth_min_c")
        death = value.get("cold_death_c")
        dormancy = value.get("cold_dormancy")
        if type(low) not in (int, float) or type(dormancy) is not bool:
            raise ValueError(f"{defname}: growth/dormancy not approved")
        if death is not None and type(death) not in (int, float):
            raise ValueError(f"{defname}: invalid cold death")
        if death is None and not dormancy:
            raise ValueError(f"{defname}: needs fixed death or dormancy")
        if death is not None and death >= low:
            raise ValueError(f"{defname}: cold death must be below growth minimum")
        if not value.get("source") or value["source"].startswith("pending"):
            raise ValueError(f"{defname}: missing balance rationale/source")
        base = f'/Defs/ThingDef[defName="{defname}"]'
        cond = ET.SubElement(ops, "li", {"Class": "PatchOperationConditional"})
        ET.SubElement(cond, "xpath").text = base + "/plant/minGrowthTemperature"
        match = ET.SubElement(cond, "match", {"Class": "PatchOperationReplace"})
        ET.SubElement(match, "xpath").text = base + "/plant/minGrowthTemperature"
        ET.SubElement(ET.SubElement(match, "value"), "minGrowthTemperature").text = str(low)
        no = ET.SubElement(cond, "nomatch", {"Class": "PatchOperationAdd"})
        ET.SubElement(no, "xpath").text = base + "/plant"
        ET.SubElement(ET.SubElement(no, "value"), "minGrowthTemperature").text = str(low)
        ext = ET.SubElement(ops, "li", {"Class": "PatchOperationAddModExtension"})
        ET.SubElement(ext, "xpath").text = base
        item = ET.SubElement(ET.SubElement(ext, "value"), "li", {"Class": "CropColdToleranceOverhaul.ColdToleranceExtension"})
        if death is not None:
            ET.SubElement(item, "coldDeathTemperature").text = str(death)
        if dormancy:
            ET.SubElement(item, "coldDormancy").text = "true"
    ET.indent(root, space="  ")
    return root

def main() -> int:
    data = json.loads(SPEC.read_text(encoding="utf-8"))
    root = make_patch(data)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {OUTPUT}; {len(data['include'])} plant definitions")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError) as err:
        print(f"NOT READY: {err}", file=sys.stderr)
        sys.exit(2)
