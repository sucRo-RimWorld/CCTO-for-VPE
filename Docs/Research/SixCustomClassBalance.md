# Six VPE custom-class crop balance — XML-only integration (2026-10-13)

This is the **owner source rationale for the six additional VPE 1.6 core PlantDefs**, with approved gameplay engineering settings in `Docs/PlantBalance.json`. The earlier [TemperatureEvidence.md](TemperatureEvidence.md) is retained as the evidence record of the original 14-plant profile and as a hashed prior-art entry; its original values remain unchanged.

All Celsius thresholds are gameplay approximations (whole-plant death, not frost damage to individual buds, flowers or roots), **not experimental universal lethal limits**. The user approved proceeding with XML-only cold compatibility for the six existing VPE classes, not rewriting them. These values remain open to reports from real VPE users.

| VPE DefName | Growth above °C | Cold death below °C | Cold dormancy | Rationale |
|---|---:|---:|---|---|
| `VCE_Peas` | 5 | −4 | no | Cool-season peas survive a light frost; min 5° is above the 40°F/4.4°C *seed-soil* guidance, but this is air temp/game balance, not a direct seed germination claim. −4° is an approximate frost-death floor, not a verified whole-plant experiment |
| `VCE_Eggplant` | 5 | −1 | no | Frost-sensitive warm crop; VPE hardcodes 0–10° soft growth multiplier and hotter 37–60° multiplier. Choosing 5° preserves growth-rate variation from 5–10°, while cold growth 0–5° is gated out; frost death−1° follows existing tomato/pepper gameplay approximation |
| `VCE_Cabbage` | 0 | −6 | no | **Exact counterpart** of CCTO MO `DankPyon_Plant_Cabbages` (0/−6); hardier than peas/eggplant and no VPE toxin behavior changes |
| `VCE_Beet` | −5 | −6 | no | VPE `Plant_WinterResistant` hardcodes the cold-growth curve beginning at −5°; use −5° native minimum so its entire curve remains accessible, with −6° severe-frost gameplay floor. Outdoor agricultural survival literature supports only *light frost* for common garden beets; −6° is **a deliberate VPE winter-resistance gameplay approximation** rather than a measured species threshold. Do not add dormancy |
| `VCE_CherryTree` | 5 | none | yes | Apply existing CCTO apple/other deciduous-fruit-tree *non-lethal cold dormancy* abstraction, preserving VPE's winter blossom artwork priority. Cherry's winter art may show flowers when internal `LeaflessNow` is true; this is not fixed by cold-tolerance XML |
| `VCE_OrangeTree` | 10 | −4 | no | **Citrus counterpart**: CCTO MO `DankPyon_Tree_Lemon` (10/−4). This is a shared citrus gameplay profile, not an experimental orange-tree kill limit; retain VPE river-growth multiplier |

## Source evidence

- [VPE 1.6 exact ThingDefs and six C# classes](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/tree/1d64cbe34a98585a29e87678dc37ea4c144f3999/1.6), reviewed in [VpeCustomPlantClassAudit.md](VpeCustomPlantClassAudit.md). The actual `Plant.TickLong` and `PlantUtility.GrowthSeasonNow` source prevent negative-season growth even when VPE Beet returns a 10% `GrowthRate`. This addon does **not** fix VPE's underlying code.
- [CCTO Medieval Overhaul canonical temperature XML](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Patches/MedievalOverhaul_ColdTolerance.xml), actual `DankPyon_Plant_Cabbages` and `DankPyon_Tree_Lemon`; static parity CI must ensure 0/−6 and 10/−4 remain identical.
- [UMN Extension cold hardiness reference](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/planting-vegetables-in-midsummer-for-fall-harvest): beets and peas generally survive high-20s °F frost; cabbage is described as hardier; these sources are relative ranking, not exact death temperatures.
- [UMN Extension crop growing and frost](https://extension.umn.edu/vegetable-growing-guides-farmers/crop-and-field-planning-tools-vegetable-farmers): eggplant frost-sensitive; beet frost tolerance depends on maturity.
- [Penn State Extension peas](https://extension.psu.edu/starting-your-summer-vegetable-garden-seeds-or-transplants): peas may germinate in 40°F soil and generally prefer cooler growing conditions; growth-min setting is game air-temperature abstraction.
- [UGA Extension eggplant](https://extension.uga.edu/publications/detail.html?number=C1028): growing season ends with frost; basis for −1° simplified death.
- [UMN Extension cherries](https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/growing-stone-fruits-in-the-home-garden): cultivars vary in overwinter hardiness; choose the existing CCTO fruit-tree model without a universal frozen whole-tree death threshold.

## Compatibility risks retained by choice

1. **VPE's own C# classes remain untouched**: Peas rain 1.5×, Eggplant heat growth bonus and 5–10°C cold ramp, Cabbage toxin resistance, Beet cold-temperature multiplier, Cherry winter bloom, Orange river boost.
2. **Beet:** documented 10% out-of-season growth rate cannot by itself bypass inherited RimWorld 1.6 `Plant.TickLong` growth-season check; modded third-party tick changes remain untested. The chosen native minimum −5° makes the VPE −5–10° factor accessible during standard growth season; no new winter override introduced.
3. **Cherry:** CCTO dormancy is an internal leafless state but VPE's custom `Graphic` prioritizes winter bloom. Loaded-game graphic/harvest behavior is **NOT RUN** and cannot be declared consistent from source analysis.
4. XML uses only `plant/minGrowthTemperature` and `ColdToleranceExtension`; it must never replace `thingClass`, manipulate special planting/fertility/harvest values or copy provider assets.
5. No in-game VPE test is required by author policy; treat static checks as source-level evidence only and investigate actual-user bug reports in [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).

Scope excludes separately installed More Plants, Mushrooms, Succulents and Flowers; those remain candidates in [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8).
