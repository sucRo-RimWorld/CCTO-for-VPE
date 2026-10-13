# CCTO for VPE — owner design (2026-10-13)

## 1. Purpose and responsibility
Create an optional separate XML-only compatibility addon that maps **Vanilla Plants Expanded (VPE) 1.6** plants to the existing **Crop Cold Tolerance Overhaul (CCTO)** per-plant minimum growth temperature, explicit cold-death threshold and low-temperature dormancy behavior.

PackageId: `sucro.cctoforvpe` (owner repository identity; not yet released). Dependency packageIds: `sucro.cropcoldtoleranceoverhaul` (CCTO), `VanillaExpanded.VPlantsE` (VPE). CCTO itself depends on Harmony and VPE on VE Framework; do not repackage these dependencies. Both providers load before this addon.

RimWorld 1.6 is the inspected supported version. VPE's inspected About.xml does not list 1.7. CCTO's own 1.7 support is insufficient to claim VPE 1.7 compatibility.

## 2. Fixed v1 scope
The **14 ordinary VPE PlantDefs** are `VCE_Grass`, `VCE_TallGrass`, `VCE_Agave`, `VCE_Onion`, `VCE_Pumpkin`, `VCE_Pepper`, `VCE_Tomato`, `VCE_AppleTree`, `VCE_PeachTree`, `VCE_PlumTree`, `VCE_PearTree`, `VCE_Opuntia`, `VCE_BearBerryBush`, `VCE_BananaTree`.

The **six VPE custom-class definitions excluded from v1** are `VCE_Peas` (`Plant_RainAffected`), `VCE_Eggplant` (`Plant_HighTempAffected`), `VCE_Cabbage` (`Plant_StopsGrowingInToxins`), `VCE_Beet` (`Plant_WinterResistant`), `VCE_CherryTree` (`Plant_WinterBlooming`), `VCE_OrangeTree` (`Plant_ChecksRiver`). Not all classes are necessarily incompatible with XML; the conservative v1 exclusion is a scope decision. Evaluate their real methods individually later.

The 14 + six coverage comes from upstream VPE 1.6 `Plants_Cultivated_Farm.xml` and `Plants_Cultivated_Trees.xml`, not a claim about unrelated other VPE add-on packs or later versions. Every listed VPE 1.6 definition has no explicit `plant/minGrowthTemperature` in its own XML; its loaded default can be inherited from parent Defs, so inspect the *loaded* value rather than assuming the source has a literal zero.

## 3. XML behavior
When complete, the addon uses a single `Patches/ColdTolerance.xml`. For each of the 14 plants:
- Set native `plant/minGrowthTemperature` through a safe existing-node replace or add when absent.
- Add exactly one `CropColdToleranceOverhaul.ColdToleranceExtension` with either `coldDeathTemperature` or `coldDormancy=true`, optionally both when independently justified.
- No changes to `thingClass`, yield, harvesting, growth days, fertility, recipes, graphics, biome generation or inventory.
- No bundled CCTO DLL, Harmony patches or fork of VPE code. Avoid duplicate extension if a third-party mod already supplies one; inspect actual loaded-mod compatibility before claiming the combined profile is safe.

CCTO keeps its 49 Vanilla and 29 MO specific PlantDefs and `MedievalOverhaul_ColdTolerance.xml`. **No MO addon or data separation**.

## 4. Source-reviewed v1 numeric balance and XML implementation

The v1 model has **source-reviewed initial engineering values**: `Docs/PlantBalance.json` is the canonical 14-species numeric table; `Docs/Research/TemperatureEvidence.md` records botanical context, existing CCTO parity and explicit gameplay approximations. The generated `Patches/ColdTolerance.xml` is the runtime patch. These numbers are **model settings, not proven universal botanical lethal temperatures or author gameplay acceptance**.

The Project VE/non-VE implementation-entry comparison and its evidence-hashed decision are in `Docs/Research/PriorArt.md` and `Docs/Research/ImplementationDecision.json`. The original VPE 1.6 14 ordinary / six custom-class exclusion remains unchanged. `Scripts/build_vpe_patch.py` is the canonical generator; tests verify the generated XML is semantically current, contains exactly one intended cold extension per ordinary plant, and refuses invalid or unapproved inputs.

**Implementation source is not release-ready runtime evidence.** Native loaded-Def counts, XPath resolution, conflict with third-party temperature patches, wild-biome survival, perennial graphics and save compatibility are still unverified pending the persistent test host.

## 5. Required test premises
1. Metadata: exact CCTO + VPE dependency IDs; VPE 1.6 target; addon loads after both; no direct MO dependency.
2. VPE 1.6 provider source: 14 ordinary DefNames, all exist exactly once and use no explicit custom `thingClass`. Six excluded custom DefNames exist and remain untouched.
3. Each approved species: correct exact XML numeric value, native growth-minimum field, one CCTO extension with correct death/dormancy semantics; never alter VPE growth/harvest/fertility/graphics.
4. CCTO-only, VPE-only, addon+both, CCTO+MO+VPE+addon profiles; clean missing-dependency handling; no duplicate extension/XPath failures.
5. Actual minimum-growth and freeze boundary checks, perennial leafless/dormant recovery, perennial no-death profiles, cold-death profiles, existing save load/re-save/add/remove; complete isolated RimWorld log with ERROR 0.
6. Static/package/source checks, no C# or runtime DLL, version and Workshop publication separately. Automated native execution uses the shared persistent Linux host only when that separate infrastructure is available.

## 6. Prior art and limitations
See `Docs/Research/PriorArt.md`; the required Project [new-module implementation gate](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/ExistingModAudit.md) still requires its formal validated decision record. Source inspection is not a native test or confirmed cold-tolerance balance.

Source bootstrap and v1 XML implementation: [issue #1](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/1), PR #2 / PR #3. Native validation and release acceptance: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).

## 7. CCTO/VPE common-plant equality contract

Where CCTO already supplies a Vanilla/MO plant matching a VPE v1 plant, **reuse exactly the existing CCTO settings** for native minimum-growth temperature, fixed cold-death temperature (if any) and cold dormancy. Do not invent an independent VPE temperature for these seven matches:

| Existing owner | CCTO PlantDef | VPE PlantDef |
|---|---|---|
| Vanilla | `Plant_Grass` | `VCE_Grass` |
| Vanilla | `Plant_TallGrass` | `VCE_TallGrass` |
| Vanilla | `Plant_Agave` | `VCE_Agave` |
| Medieval Overhaul | `DankPyon_Plant_Onions` | `VCE_Onion` |
| Medieval Overhaul | `DankPyon_Plant_Pumpkins` | `VCE_Pumpkin` |
| Medieval Overhaul | `DankPyon_Plant_Tomatoes` | `VCE_Tomato` |
| Medieval Overhaul | `DankPyon_Tree_Apple` | `VCE_AppleTree` |

`Tests/test_ccto_parity.py` extracts actual XML values from [CCTO main](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul) and compares them to this addon's committed XML and `Docs/PlantBalance.json`. The GitHub Actions workflow checks out the two current upstream `Patches/*.xml` files using sparse checkout; missing files, duplicate rules, mismatched conditional branches and differences in any of the three properties **fail CI**. A local test without CCTO source may skip this cross-repo test, but CI sets `CCTO_PARITY_REQUIRED=1` so it cannot skip. For local execution, set `CCTO_SOURCE_ROOT` to a CCTO checkout. The CI workflow may also be invoked manually after upstream CCTO changes; an upstream-only push does not automatically trigger this repository's CI.

These are **distinct PlantDefs** with matched values, not interchangeable XML targets. The other seven VPE v1 species retain independently documented values. Source-parity PASS alone is not a RimWorld loaded-game, crop-dormancy or save-compatibility PASS.
