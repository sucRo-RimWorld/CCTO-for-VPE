# CCTO for VPE Coordination — main only

This file is for cross-workstream state and handoffs only. Values, behavior and release policy are authoritative in `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/TemperatureEvidence.md`, `Docs/ReleaseChecklist.md`, and `Patches/ColdTolerance.xml`.

## VPE-COMMUNITY-VALIDATION-20261013

**Owner:** CCTO for VPE.
**Status:** V1 XML IMPLEMENTED; STATIC/PARITY CI PASS; **NATIVE GAMEPLAY NOT RUN; USER BUG REPORTS ADOPTED**. Author Workshop release has not been performed.

- Author explicitly does not use VPE. For CCTO for VPE **only**, mandatory pre-release native RimWorld testing is waived. After users try the addon, bugs and compatibility issues will be handled through the repository [issue tracker](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues), with a bilingual report template; [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4) owns follow-up. No reports is not native PASS.
- Still required before release: successful static 20 included (14 ordinary + six custom class) Def, XML/data and nine CCTO Vanilla/MO counterpart parity checks; source/dependency validation; bilingual disclosure of the untested-gameplay state; clean actual subscriber payload and author-controlled Steam upload. No 1.7 VPE compatibility asserted.
- CCTO keeps the Vanilla + Medieval Overhaul mappings/framework. No numeric, runtime XML or dependency change is authorized by this reporting-policy change.
- Shared persistent host remains the project direction for any *optional* later VPE native reproduction, not an unresolved release prerequisite for this addon.

## VPE-ADDON-OWNERSHIP-20261013

**Owner:** CCTO for VPE (single compatibility addon for the VPE plant-provider ecosystem).
**Status:** AUTHOR APPROVED SINGLE OWNER; FOUR UPSTREAM VPE CHILD PACKS INVENTORIED AS **UNSUPPORTED CANDIDATES**; implementation of additional patch XML OPEN in [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8).

- The original 14+6 VPE v1 inventory has been expanded to 20 included / 0 excluded base VPE 1.6 Defs, with nine CCTO counterpart parity checks. No new temperature XML, new package dependencies or native tests in this decision.
- Four detected modules: More Plants, Mushrooms, Succulents, Flowers (source revisions recorded in `Docs/AddonInventory.json`); confirm exact provider identity and custom/ordinary classes before each conditional patch. CCTO base is **not** the owner of VPE family addon definitions.
- Community bug reports/optional native reproduction remain with issue #4; do not treat VPE game tests as a publication prerequisite. Design/source-of-truth: `Docs/Design.md §8`, `Docs/AddonCompatibility.md`.

## VPE-SIX-CUSTOM-CLASS-SOURCE-AUDIT-20261013

**Owner:** CCTO for VPE original VPE v1 plant scope.
**Status:** SOURCE INSPECTION COMPLETE — **6/6 native growth-minimum + CCTO cold-death extension XML-ADDRESSABLE**, SIX EXTRA CUSTOM-CLASS PLANTS NOW SOURCE-IMPLEMENTED WITH ENGINEERING VALUES; NATIVE GAMEPLAY UNVERIFIED.

Verified VPE 1.6 custom class methods, RimWorld 1.6 Plant.TickLong and PlantUtility.GrowthSeasonNow, and CCTO's base Plant Harmony hooks. Eggplant/Beet retain hardcoded growth multipliers; Beet's documented 10% out-of-season growth-rate return is blocked by base TickLong actual growth gating; Cherry winter blossom graphics override leafless priority. VPE special behavior remains unchanged; CCTO compatibility source values are in `Docs/PlantBalance.json` and `Docs/Research/SixCustomClassBalance.md`. Exact class evidence and limitations in `Docs/Research/VpeCustomPlantClassAudit.md`, completed source XML implementation in [issue #10](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/10). No actual loaded-game testing or steam distribution performed.

## VPE-CUSTOM-SIX-XML-INTEGRATION-20261013

**Owner:** CCTO for VPE core PlantDefs. **Status:** SOURCE XML FOR 20 VPE BASE PLANTS; 6/6 PREVIOUSLY DEFERRED CLASS TARGETS NOW INCLUDED; CCTO PARITY EXPANDED TO 9; NATIVE GAMEPLAY UNVERIFIED.

PlantBalance.json owns added numerical decisions; [SixCustomClassBalance](Research/SixCustomClassBalance.md) owns six-class justification. Generator and static suite now validate 20 core XML targets and preserved `thingClass` identities without adding C#. CCTO base Vanilla/MO remains untouched; optional More Plants/Mushrooms/Succulents/Flowers are still only candidate packs in issue #8. Native testing remains waived by author and bug reporting #4. No Steam publication performed.
