# CCTO for VPE Coordination — main only

This file is for cross-workstream state and handoffs only. Values, behavior and release policy are authoritative in `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/TemperatureEvidence.md`, `Docs/ReleaseChecklist.md`, and `Patches/ColdTolerance.xml`.

## VPE-COMMUNITY-VALIDATION-20261013

**Owner:** CCTO for VPE.
**Status:** V1 XML IMPLEMENTED; STATIC/PARITY CI PASS; **NATIVE GAMEPLAY NOT RUN; USER BUG REPORTS ADOPTED**. Author Workshop release has not been performed.

- Author explicitly does not use VPE. For CCTO for VPE **only**, mandatory pre-release native RimWorld testing is waived. After users try the addon, bugs and compatibility issues will be handled through the repository [issue tracker](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues), with a bilingual report template; [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4) owns follow-up. No reports is not native PASS.
- Still required before release: successful static 14 included / six excluded Def, XML/data and seven shared Vanilla/MO parity checks; source/dependency validation; bilingual disclosure of the untested-gameplay state; clean actual subscriber payload and author-controlled Steam upload. No 1.7 VPE compatibility asserted.
- CCTO keeps the Vanilla + Medieval Overhaul mappings/framework. No numeric, runtime XML or dependency change is authorized by this reporting-policy change.
- Shared persistent host remains the project direction for any *optional* later VPE native reproduction, not an unresolved release prerequisite for this addon.

## VPE-ADDON-OWNERSHIP-20261013

**Owner:** CCTO for VPE (single compatibility addon for the VPE plant-provider ecosystem).
**Status:** AUTHOR APPROVED SINGLE OWNER; FOUR UPSTREAM VPE CHILD PACKS INVENTORIED AS **UNSUPPORTED CANDIDATES**; implementation of additional patch XML OPEN in [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8).

- Preserve existing 14+6 base VPE v1 data and seven current CCTO Vanilla/MO counterparts. No new temperature XML, new package dependencies or native tests in this decision.
- Four detected modules: More Plants, Mushrooms, Succulents, Flowers (source revisions recorded in `Docs/AddonInventory.json`); confirm exact provider identity and custom/ordinary classes before each conditional patch. CCTO base is **not** the owner of VPE family addon definitions.
- Community bug reports/optional native reproduction remain with issue #4; do not treat VPE game tests as a publication prerequisite. Design/source-of-truth: `Docs/Design.md §8`, `Docs/AddonCompatibility.md`.
