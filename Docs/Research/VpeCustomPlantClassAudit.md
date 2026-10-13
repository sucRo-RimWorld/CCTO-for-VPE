# VPE core — six custom-class plants and CCTO XML compatibility (2026-10-13)

## Source and scope

**Finding:** The six VPE 1.6 custom-class plants excluded from CCTO for VPE's initial **14-plant** XML patch can all be targeted using XML for `plant/minGrowthTemperature` and CCTO's `ColdToleranceExtension` (cold death and, if appropriate, dormancy). VPE uses custom subclasses of `RimWorld.Plant`, but none of these six source classes overrides `TickLong()`, `MakeLeafless()` or `CheckMakeLeafless()`. Exclusion was a conservative v1 scope choice, **not proof that XML cannot work**.

This is a **source audit**, not a loaded RimWorld compatibility test. The author waives mandatory VPE native testing and will use player bug reports. This report documents **original feasibility evidence**. A subsequent source-controlled expansion has now added six reviewed numeric profiles and XML mappings, making **20 included / zero excluded core VPE plants**. The original 14 values remain unchanged, and CCTO value parity checks now cover nine VPE counterparts. See [SixCustomClassBalance.md](SixCustomClassBalance.md) for current six-species decisions; still no native RimWorld gameplay test.

Inspected source versions:
- [VPE 1.6 farm and tree Defs](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/tree/1d64cbe34a98585a29e87678dc37ea4c144f3999/1.6/Defs/ThingDefs_Plants) and [six original class implementations](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/tree/1d64cbe34a98585a29e87678dc37ea4c144f3999/1.6/Source/VanillaPlantsExpanded/VanillaPlantsExpanded/Plant%20Classes), source repository main `1d64cbe34a98585a29e87678dc37ea4c144f3999`.
- RimWorld `Plant.cs` and `PlantUtility.cs` from [decompiled build `1.6.4850 rev645`](https://github.com/codexvn/RimWorldDecompiled), [Plant.cs](https://github.com/codexvn/RimWorldDecompiled/blob/main/Assembly-CSharp/RimWorld/Plant.cs), [PlantUtility.cs](https://github.com/codexvn/RimWorldDecompiled/blob/main/Assembly-CSharp/RimWorld/PlantUtility.cs). Decompiled material is used only as an inspection reference and is **not** copied into the Mod.
- [CCTO base Plant Harmony patches](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Source/CropColdToleranceOverhaul/Patches/PlantColdTolerancePatches.cs) and [CCTO extension](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Source/CropColdToleranceOverhaul/ColdToleranceExtension.cs).

## Why the minimum growth temperature remains effective

- Both `PlantUtility.GrowthSeasonNow(Map, ThingDef)` and `PlantUtility.GrowthSeasonNow(IntVec3, Map, ThingDef)` check the species' **actual Def field** `plant.minGrowthTemperature`; the cell-specific check requires temperature **strictly above** that minimum and below `plant.maxGrowthTemperature`.
- The inherited `Plant.TickLong()` increments actual growth only **if `GrowthSeasonNow` is true**. It then uses `GrowthPerTick`, which multiplies the plant's own virtual `GrowthRate`.
- The standard `Plant.GrowthRateFactor_Temperature` reads `PlantUtility.GrowthRateFactorFor_Temperature(def,temp)`, whose interpolation uses `minGrowthTemperature` and `minOptimalGrowthTemperature`.
- Custom `GrowthRate` expressions or custom temperature multipliers **do not bypass `Plant.TickLong`'s actual growth gate**. A property returning a nonzero growth rate when `GrowthSeasonNow` is false need not imply actual growth.
- CCTO sets the cold-leafless threshold, intercepts cold `MakeLeafless` calls and checks `CheckMakeLeafless` on the **base `Plant`**; each of the six classes inherits these members. CCTO's Def extension is resolved using `plant.def.GetModExtension<ColdToleranceExtension>()`, independently of the specific VPE subclass.

## Class-by-class findings

| VPE ThingDef | Actual C# special behavior | XML growth minimum | CCTO cold-death XML | Caveat for dormancy / native play |
|---|---|---|---|---|
| `VCE_Peas` | `Plant_RainAffected`: native temperature factor; rain multiplies growth by 1.5 | **Yes** | **Yes** | Preserve rainfall effect and VPE graphics |
| `VCE_Eggplant` | `Plant_HighTempAffected`: explicit 0–10°C and hot 37–60°C multiplier in C# | **Yes** via `GrowthSeasonNow` | **Yes** | XML changes growth/no-growth cutoff but **not** the hardcoded multiplier curve. Retain heat bonus |
| `VCE_Cabbage` | `Plant_StopsGrowingInToxins`: native temperature factor; toxic-fallout growth pause | **Yes** | **Yes** | Preserve custom toxin rule and `dieFromToxicFallout=false` |
| `VCE_Beet` | `Plant_WinterResistant`: explicit −5–10°C factor and `GrowthRate=0.1` when out of season | **Yes** via inherited tick gate | **Yes** | Critical discrepancy: base `Plant.TickLong` will not add growth when `GrowthSeasonNow=false`, despite custom `GrowthRate` returning 0.1; this apparent VPE winter-growth mismatch is independent of CCTO. Avoid cold dormancy that unnecessarily overrides intended winter-resistant design |
| `VCE_CherryTree` | `Plant_WinterBlooming`: winter-blossom `Graphic` chosen before checking `LeaflessNow` | **Yes** | **Yes** | Cold dormancy may internally mark it leafless but winter blossom remains visible. Avoid claiming visual dormancy fidelity merely from XML |
| `VCE_OrangeTree` | `Plant_ChecksRiver`: native temperature factor and local river-tile growth multiplier | **Yes** | **Yes** | Keep river and perennial fruit-tree behavior |

**Temperature consistency:** Vanilla native growth depends on both `minGrowthTemperature` and the max-growth threshold. For Eggplant/Beet, their VPE hardcoded multiplier remains unchanged and only the outer growth-eligibility boundary changes with XML. Do not present the hardcoded curve as dynamically reparameterized.

**Important limitation:** A numeric `minGrowthTemperature` field being applied in XML does **not** guarantee that the plant's custom `GetInspectString()`, winter blossom graphics, or inherited harvest rules present a fully consistent player-facing picture. No VPE native game validation, harvest-in-winter behavior, or conflicting third-party Harmony patch compatibility was established in this audit.

## Implementation implications

1. The single CCTO for VPE addon now supports all six in source XML by adding `minGrowthTemperature` and a `ColdToleranceExtension` per exact DefName, **without changing `thingClass` or adding a C# assembly**, under the per-plant balance decisions in [SixCustomClassBalance.md](SixCustomClassBalance.md).
2. **CCTO cold-death threshold** is XML-addressable for all six; `coldDormancy` is a per-plant design decision, not universally appropriate (especially Beet and Cherry).
3. Preserve CCTO base Vanilla/MO numeric ownership, VPE's rain/toxin/river/heat/graphic behavior, and source-validation gates. Core source checks now assert 20 included and zero excluded, and runtime/native behavior remains unverified; do not advertise compatibility for separate VPE child packs.
4. Source implementation tracked at [issue #10](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/10); future separate VPE-family packs at [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8); player-reported bugs at [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).
