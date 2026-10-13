# CCTO for VPE — prior-art comparison (2026-10-13)

## Goal
A **small, optional, XML-only distribution** giving VPE plants CCTO's distinct cold-death and dormancy rules without forcing VPE, the VPE framework or its other content into the base CCTO package. Scope: VPE 1.6 14 ordinary Defs, six custom classes deferred. This is **compatibility with two existing mods**, not a new growing-system framework.

## Compared upstreams
| Ecosystem | Candidate and actual source | Function and overlap | Dependency/maintenance conclusion |
|---|---|---|---|
| Vanilla/MO | RimWorld native `PlantProperties.minGrowthTemperature`; [CCTO Framework](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Docs/Framework.md); existing CCTO [MO XML](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Patches/MedievalOverhaul_ColdTolerance.xml) | Native growth minimum exists but separate cold-death threshold/dormancy is implemented by CCTO. MO plant values are already supplied by CCTO. | Reuse existing framework, do not reimplement C#, no MO separation. |
| VE | [Vanilla Plants Expanded 1.6 Defs](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/tree/main/1.6/Defs/ThingDefs_Plants), [About.xml](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/blob/main/About/About.xml) | Adds 20 cultivated plants/trees in the inspected pair of XML files; 14 default-class and six custom class. No per-species CCTO extensions in those inspected files. | Keep VPE intact and optional; XML patch only, 14 explicit DefNames. Must retain VPE + VEF dependencies without reproducing code/art. |
| Existing AMJ | [Project CCTO compatibility boundaries](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/CCTOCompatibilityLayers.md) | AMJ owners implement their own plant data, not VPE; CCTO core owns Vanilla/MO. | New owner `CCTO-for-VPE` for VPE-only mapping; no data duplication. |
| Non-VE | [Expandable Plants (Continued)](https://github.com/emipa606/ExpandablePlants) / [Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2958061468) | Exposes plant leafless/growth ranges and other hardcoded controls to XML; not verified to supply a complete VPE-to-CCTO per-species temperature table. | Different/extensible framework; do not make another runtime dependency for narrow CCTO consumer XML. License/content not copied. |
| Non-VE | [Winter Plants! (Continued)](https://steamcommunity.com/sharedfiles/filedetails/?id=3381148792) | Adds winter crops; does not establish that existing VPE crops receive distinct CCTO thresholds. | Additional crop pack, not a replacement for VPE-specific cold values. No dependency. |
| Non-VE | [Heat of the Desert](https://steamcommunity.com/sharedfiles/filedetails/?id=2884644198) | Heat-related environment/animal/plant effects, not the same targeted VPE cold-death/dormancy mapping. | Different scope, not a substitute. |

## Evaluation
- **Function:** CCTO already provides the engine; a small set of external XML patches is the missing link. VPE adds crop content but no CCTO compatibility in the inspected plant Defs.
- **Historical/cultural fit:** not a Japanese-culture rewrite; leave VPE plants, names and graphics unchanged. Species-specific cold hardiness requires independent evidence.
- **Dependencies:** package requires CCTO and VPE, neither bundled; using Expandable Plants would add a redundant framework dependency.
- **Content retention:** all existing VPE content remains; no recipes, plant graphics, yields or special six-class behavior disabled.
- **Progression/balance:** no farming progression changes, but minimum-growth/cold-death/seasonality can affect production; values pending individual review.
- **Reuse/maintenance/license:** CCTO XML API reused; no 3rd-party source/assets copied, only DefName references. VPE updates/version mismatch require re-audit.

**Decision for this research stage:** optional compatibility is narrower than shipping CCTO itself with VPE patches, and preferable to custom C# or importing another plant framework. VE and non-VE alternatives above were compared using public descriptions and explicitly linked source; not all installed Workshop overrides, exact licensing documents or final load-order interactions have been inspected. The Project formal JSON decision/evidence SHA256 validator has **not yet been completed**; production XML/value promotion stays HOLD until that gate is satisfied. This is not a claim of exhaustive Mod coverage.
