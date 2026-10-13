# CCTO for VPE — owner design (2026-10-13)

## 1. Purpose and responsibility
Create an optional separate XML-only compatibility addon that maps **Vanilla Plants Expanded (VPE) 1.6** plants to the existing **Crop Cold Tolerance Overhaul (CCTO)** per-plant minimum growth temperature, explicit cold-death threshold and low-temperature dormancy behavior.

PackageId: `sucro.cctoforvpe` (owner repository identity; not yet released). Dependency packageIds: `sucro.cropcoldtoleranceoverhaul` (CCTO), `VanillaExpanded.VPlantsE` (VPE). CCTO itself depends on Harmony and VPE on VE Framework; do not repackage these dependencies. Both providers load before this addon.

RimWorld 1.6 is the inspected supported version. VPE's inspected About.xml does not list 1.7. CCTO's own 1.7 support is insufficient to claim VPE 1.7 compatibility.

## 2. Original v1 scope and expanded 20-plant base VPE implementation
The **14 ordinary VPE PlantDefs** are `VCE_Grass`, `VCE_TallGrass`, `VCE_Agave`, `VCE_Onion`, `VCE_Pumpkin`, `VCE_Pepper`, `VCE_Tomato`, `VCE_AppleTree`, `VCE_PeachTree`, `VCE_PlumTree`, `VCE_PearTree`, `VCE_Opuntia`, `VCE_BearBerryBush`, `VCE_BananaTree`.

The **six VPE custom-class definitions originally excluded from v1 but now included in the XML-only expansion** are `VCE_Peas` (`Plant_RainAffected`), `VCE_Eggplant` (`Plant_HighTempAffected`), `VCE_Cabbage` (`Plant_StopsGrowingInToxins`), `VCE_Beet` (`Plant_WinterResistant`), `VCE_CherryTree` (`Plant_WinterBlooming`), `VCE_OrangeTree` (`Plant_ChecksRiver`). All six were **subsequently inspected** against VPE 1.6 custom-class sources, RimWorld 1.6 growth-season and tick logic, and CCTO's base-Plant hooks. Their native minimum-growth temperature and CCTO cold-death extension are XML-addressable without a C# fork; the historical six exclusions were a **v1 release-scope choice**, not an inherent XML limitation; they are now explicitly included with owner values documented in [SixCustomClassBalance](Research/SixCustomClassBalance.md). Independent hot/cold growth factors (eggplant/beet), cherry winter blossom graphics, and beet's apparent out-of-season 10% growth-rate/tick mismatch require semantics-preserving decisions. See [special-class source audit](Docs/Research/VpeCustomPlantClassAudit.md) and [issue #10](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/10).

The original 14 + six inventory (now 20 included) comes from upstream VPE 1.6 `Plants_Cultivated_Farm.xml` and `Plants_Cultivated_Trees.xml`, not a claim about unrelated other VPE add-on packs or later versions. Every listed VPE 1.6 definition has no explicit `plant/minGrowthTemperature` in its own XML; its loaded default can be inherited from parent Defs, so inspect the *loaded* value rather than assuming the source has a literal zero.

## 3. XML behavior
When complete, the addon uses a single `Patches/ColdTolerance.xml`. For each of the 20 base VPE plants:
- Set native `plant/minGrowthTemperature` through a safe existing-node replace or add when absent.
- Add exactly one `CropColdToleranceOverhaul.ColdToleranceExtension` with either `coldDeathTemperature` or `coldDormancy=true`, optionally both when independently justified.
- No changes to `thingClass`, yield, harvesting, growth days, fertility, recipes, graphics, biome generation or inventory.
- No bundled CCTO DLL, Harmony patches or fork of VPE code. Avoid duplicate extension if a third-party mod already supplies one; inspect actual loaded-mod compatibility before claiming the combined profile is safe.

CCTO keeps its 49 Vanilla and 29 MO specific PlantDefs and `MedievalOverhaul_ColdTolerance.xml`. **No MO addon or data separation**.

## 4. Source-reviewed v1 numeric balance and XML implementation

The v1 model has **source-reviewed initial engineering values**: `Docs/PlantBalance.json` is the canonical 20-species numeric table; `Docs/Research/TemperatureEvidence.md` preserves the original 14-plant rationale and [SixCustomClassBalance](Research/SixCustomClassBalance.md) documents the extra six with source evidence and explicit gameplay approximations. The generated `Patches/ColdTolerance.xml` is the runtime patch. These numbers are **model settings, not proven universal botanical lethal temperatures or author gameplay acceptance**.

The Project VE/non-VE implementation-entry comparison and its evidence-hashed decision are in `Docs/Research/PriorArt.md` and `Docs/Research/ImplementationDecision.json`. The initial 14 ordinary / six deferred custom-class split has since been extended to include all six with preserved custom `thingClass` implementations, without broadening to separate VPE child packs. `Scripts/build_vpe_patch.py` is the canonical generator; tests verify the generated XML is semantically current, contains exactly one intended cold extension per included plant (including six custom-class targets), and refuses invalid or unapproved inputs.

**Runtime evidence remains absent.** The author does not use VPE, so mandatory pre-publication native gameplay testing is waived specifically for CCTO for VPE. Instead, users who actually play with VPE provide post-distribution bug reports. Absence of reports is **not** proof of functioning loaded Defs, XPath resolution, save compatibility, graphics, or survival; static CI alone never establishes native PASS.

## 5. Validation and user-reporting policy (2026-10-13)

**Author decision:** Since the author does not play with Vanilla Plants Expanded (VPE), do **not** block the initial CCTO for VPE distribution on an author-operated in-game test. Use static/source validation before distribution, and investigate/reproduce problems from actual VPE users' bug reports afterward. This exception applies only to this optional addon, not to CCTO's established Vanilla/MO tests or other AMJ modules.

### Before any Workshop distribution — mandatory checks
1. Exact packageIds: addon `sucro.cctoforvpe`, CCTO `sucro.cropcoldtoleranceoverhaul`, VPE `VanillaExpanded.VPlantsE`. RimWorld 1.6 only until VPE 1.7 is separately verified.
2. Exact 20 included VPE 1.6 DefNames (14 ordinary plus six verified custom-class); matching source XML structure, one extension per target and expected native growth-minimum/cold-death/dormancy values. Do not change VPE class, yield, harvest, fertility, graphics or recipes.
3. All repository CI on the **exact release source** succeeds, including canonical balance/XML equality, evidence hashes and equality of the nine VPE counterparts with *current CCTO main* values. Preserve lack of native validation in the released English/Japanese description.
4. Inspect the final **subscriber** package (dependencies/identity/runtime XML present; no development files, sources, extra DLL or copied VPE/CCTO assets). Workshop uploading, permissions and actual subscriber download verification remain separate from GitHub CI.

### Community-based post-distribution validation
- Publish a visible bug-report route to [GitHub Issues](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues), with a bilingual [report template](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose). Workshop comments may also identify issues; capture actionable follow-up in the owning issue tracker without asking the author to relay reports between agents.
- For a useful report, request RimWorld/VPE/VEF/CCTO/addon versions, game error log and Mod list or load order where practical, affected plant, expected/actual cold/dormancy behavior, steps/temperature/season, and any possible conflicting plant temperature patches. Do **not** require users to publish private saves, account details, or personal information.
- Triage, reproduce deterministically where possible (XML/source investigation first; shared native host only if actually available and justified), fix via a scoped PR, run affected static gates, then document fix/version and ask the reporter to confirm if practical. Do not mark a bug fixed based solely on a speculative XML change or absence of new reports.
- The decision to accept user-reported problems does **not** imply that unreported bugs are absent. Log native/load/save/visual evidence as **NOT RUN / UNVERIFIED** until independently observed. Release notes must not claim actual RimWorld runtime PASS.

### Optional diagnostic scenarios (not a release gate)
If a report requires real-game reproduction, investigate VPE/VEF/Harmony/CCTO provider loading, patch XPath failures, 20 included Defs (including six custom-class Defs), cold-boundary changes, grass/fruit-tree dormancy and recovery, winter graphics, wild-plant die-off, third-party duplicate extensions, and save add/remove. An actual native test, if performed, must capture isolated complete ERROR logs and provider identity; an incomplete run may never be called PASS.

## 6. Prior art and limitations
See `Docs/Research/PriorArt.md`; the required Project [new-module implementation gate](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/ExistingModAudit.md) still requires its formal validated decision record. Source inspection is not a native test or confirmed cold-tolerance balance.

Source bootstrap and v1 XML implementation: [issue #1](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/1), PR #2 / PR #3. Post-distribution user bug reports and optional reproduction: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).

## 7. CCTO/VPE common-plant equality contract

Where CCTO already supplies a Vanilla/MO plant matching a VPE v1 plant, **reuse exactly the existing CCTO settings** for native minimum-growth temperature, fixed cold-death temperature (if any) and cold dormancy. Do not invent an independent VPE temperature for these nine matches (the original seven plus cabbage and citrus-orange):

| Existing owner | CCTO PlantDef | VPE PlantDef |
|---|---|---|
| Vanilla | `Plant_Grass` | `VCE_Grass` |
| Vanilla | `Plant_TallGrass` | `VCE_TallGrass` |
| Vanilla | `Plant_Agave` | `VCE_Agave` |
| Medieval Overhaul | `DankPyon_Plant_Onions` | `VCE_Onion` |
| Medieval Overhaul | `DankPyon_Plant_Pumpkins` | `VCE_Pumpkin` |
| Medieval Overhaul | `DankPyon_Plant_Tomatoes` | `VCE_Tomato` |
| Medieval Overhaul | `DankPyon_Tree_Apple` | `VCE_AppleTree` |
| Medieval Overhaul | `DankPyon_Plant_Cabbages` | `VCE_Cabbage` |
| Medieval Overhaul (citrus analogue) | `DankPyon_Tree_Lemon` | `VCE_OrangeTree` |

`Tests/test_ccto_parity.py` extracts actual XML values from [CCTO main](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul) and compares them to this addon's committed XML and `Docs/PlantBalance.json`. The GitHub Actions workflow checks out the two current upstream `Patches/*.xml` files using sparse checkout; missing files, duplicate rules, mismatched conditional branches and differences in any of the three properties **fail CI**. A local test without CCTO source may skip this cross-repo test, but CI sets `CCTO_PARITY_REQUIRED=1` so it cannot skip. For local execution, set `CCTO_SOURCE_ROOT` to a CCTO checkout. The CI workflow may also be invoked manually after upstream CCTO changes; an upstream-only push does not automatically trigger this repository's CI.

These are **distinct PlantDefs** with matched values, not interchangeable XML targets. The other eleven included VPE 1.6 plants retain independently documented values; the orange/lemon relation is a citrus-family **gameplay analogue**, not identical species. Source-parity PASS alone is not a RimWorld loaded-game, crop-dormancy or save-compatibility PASS.

## 8. One compatibility owner for the VPE plant-addon ecosystem (2026-10-13)

**Author decision:** CCTO for VPE is the **only CCTO compatibility Mod** responsible for VPE base and the plant-adding VPE family of addons. Do **not** split each optional VPE addon into yet another independent patch Mod or expand the CCTO base package. This is a long-term ownership/scope decision, not an assertion of comprehensive implementation today.

The separately loaded related VPE plant packs identified from their upstream 1.6 repositories are **More Plants**, **Mushrooms**, **Succulents**, and **Flowers**. Their exact upstream names, source refs, status, and review limitations are in `Docs/AddonInventory.json`; the canonical future implementation procedure is `Docs/AddonCompatibility.md`. Third-party plant additions explicitly built for VPE may also be reviewed under this owner; unrelated Vanilla Expanded features, recipes, mechanics or whole-mod compatibility are outside scope.

**Backward compatibility:** `Docs/PlantBalance.json`, `Patches/ColdTolerance.xml` and existing regression tests remain strictly for the current 20 source-implemented base VPE PlantDefs (14 ordinary and six verified custom class). All four additional packs are **candidates only, without temperature XML or approved numeric values**. Do not alter current production XML or advertise addon crop support before per-pack source/Def audit.

Future per-pack patches live in separate `Patches/Addons/<Pack>.xml`, generated from owner-only approved per-pack data and guarded by exact checked provider identification (e.g., `PatchOperationFindMod`). Only execute XML targeting plants when the corresponding optional provider is active. **VPE core and CCTO remain the only hard dependencies** in `About/About.xml`; new packs are not required for other packs to function. If no relevant VPE pack is installed, no extra patch is evaluated. The goal is bounded startup overhead; do not claim benchmarked performance savings.

Each add-on is reviewed **by its own verified provider DefNames and class semantics**: eligible ordinary PlantDefs first; custom `thingClass`, special growing zones, DLC-gated plants and dynamic/growth-transforming classes require case-specific investigation and may be deferred. Preserve class behaviors, growth/harvest, world generation, and no double extensions. Reuse identical CCTO Vanilla/MO temperature values for equivalent plants, with source parity checks. Do not copy VPE or third-party source assets.

The [Project VE/non-VE audit](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/ExistingModAudit.md) applies when a new *substantive* behavior/framework is proposed; extending already-approved CCTO XML mappings still requires provider/source and numeric-balance evidence. The author continues to waive mandatory author-operated native RimWorld tests specifically for this optional compatibility Mod; source CI, real subscriber payload checks, accurate supported-pack labeling and player bug-report handling remain in force. Active expansion tracking: [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8); user reports: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).

## 9. Six originally deferred custom-class VPE plants — XML implementation

The source-level feasibility [audit](Research/VpeCustomPlantClassAudit.md) and per-species [balance evidence](Research/SixCustomClassBalance.md) underpin the six added production XML targets. `Docs/PlantBalance.json` now has **20 included / zero excluded** core-VPE plants and a `custom_classes` identity map recording the original six actual VPE C# subclasses. CCTO base class hooks cover the added death/dormancy extension; `PlantUtility.GrowthSeasonNow` and inherited `Plant.TickLong` read native minimum-growth thresholds. Neither VPE nor CCTO source/C# is modified here. For Cherry, the non-lethal dormancy model follows the existing orchard trees, despite winter blossoms taking rendering precedence; for Beet, avoid dormancy and retain its VPE winter-resistance temperature factor. This does **not** add compatibility for separately installed VPE family packs or validate gameplay in a running game. Original 14-species numeric settings stay unchanged; CCTO value parity increases from seven to **nine** source-checked counterpart pairs.
