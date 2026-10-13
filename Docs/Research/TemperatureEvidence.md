# VPE v1 temperature-balance evidence and limitations (2026-10-13)

These values are **RimWorld game-balance decisions**, not universal species lethal-temperature experiments. Minimum growth temperature describes the CCTO/RimWorld model and is **not identical to seed germination minimum**. Cold death is a whole-plant gameplay state, not flower-bud damage; perennial dormancy deliberately omits a lethal threshold when the CCTO existing model does so.

## Source inventory
- [Existing CCTO design (Vanilla/MO exact comparisons)](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Docs/Design.md) — the actual already-owned Onion 5/-3, Pumpkin 10/-1, Tomato 10/-1, Apple 5/dormancy, Agave 5/-7 and Grass/Tall grass 0/dormancy; retrieved 2026-10-13.
- [VPE 1.6 farm XML](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Farm.xml), blob f7d4ee072fb3459c33bb047c1541bd2012d393f3; [VPE tree XML](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Trees.xml), blob 01cbeb243b0c7582696267af70ade44c92477d67 — both inspected for the 14 ordinary / six custom classes; no explicit native min-growth temperatures on these 20 definitions. Parent-class/inheritance effects remain loaded-game test scope.
- [Penn State Extension seed/seedling biology](https://extension.psu.edu/seed-and-seedling-biology) — seed germination min: onion 35°F, tomato 50°F, pepper/pumpkin 60°F; used **for relative warmth ordering only**, not as direct in-game air-temperature readings.
- [University of Georgia fruit-tree cold stages](https://site.extension.uga.edu/gardener/2025/02/critical-temperatures-for-fruit-trees/) — dormant peach/plum/pear buds withstand colder weather than flower buds; flower-bud damage is not whole-plant death.
- [Apple/pear low-temperature dormancy study](https://pubmed.ncbi.nlm.nih.gov/15519992/) — temperature below 12°C triggers apple/pear dormancy stages in studied cultivars; 5°C as the *game threshold* follows existing CCTO Apple rather than claiming a measured universal species cutoff.
- [University of Minnesota northern forest recommendations](https://extension.umn.edu/recommended-trees/recommended-trees-region-4) and [bearberry classification](https://plantsearch.extension.umn.edu/searchplants/list?goto=6) — bearberry is a northern cold-adapted evergreen shrub; do not make it leafless with `coldDormancy`. The -40°C lethal setting is an **explicit game abstraction, not a documented all-variety survival threshold**.
- [UF/IFAS banana growing guide](https://ask.ifas.ufl.edu/publication/MG040?downloadOpen=true) — growth slows below 16°C, freezes at/below 0°C, <-2°C can destroy aboveground plant; rhizomes may resprout. VPE's persistent banana TreeDef does not model that regrowth, hence simplified fatal threshold -2°C.
- [UA agave climatic range](https://www.extension.arizona.edu/publication/arizona-climate-zones-and-their-application-growing-plants) — cold resilience differs materially by agave species; the VPE generic "agave" has no identified species, so copy CCTO's existing generic Agave values rather than claim a true universal survival limit.
- [VPE generic opuntia description](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Trees.xml) — the genus/cultivar is not specified, so 8/-8 is a **moderate desert gameplay profile** rather than proven physiological minimum. Treat it as a named review risk.

## Adopted v1 engineering balance (°C)
| VPE Def | Growth >= | Death below | Dormancy below growth | Basis |
|---|---:|---:|---|---|
| `VCE_Grass` | 0 | none | yes | CCTO generic Grass 0°C cold dormancy, analogous grazing perennial; species unspecified. |
| `VCE_TallGrass` | 0 | none | yes | CCTO Tall grass 0°C cold dormancy; leaves disappear over winter as VPE has leafless graphic. |
| `VCE_Agave` | 5 | -7 | no | CCTO Vanilla Agave exact 5/-7 balance; genus and cultivars vary in natural hardiness. |
| `VCE_Onion` | 5 | -3 | no | CCTO Medieval Overhaul Onion exact 5/-3 balance; avoids two conflicting Onion profiles. |
| `VCE_Pumpkin` | 10 | -1 | no | CCTO Medieval Overhaul Pumpkin exact 10/-1 and PSU warm-season germination. |
| `VCE_Pepper` | 12 | -1 | no | PSU pepper minimum seed germination 60°F (15.6°C), warmer than tomato 50°F; 12°C gameplay growth cutoff; -1°C frost damage approximation. |
| `VCE_Tomato` | 10 | -1 | no | CCTO Medieval Overhaul Tomato exact 10/-1; PSU seeds more warm-sensitive than onions. |
| `VCE_AppleTree` | 5 | none | yes | CCTO Medieval Overhaul Apple exact 5°C cold dormancy; apple/pear dormancy response research. |
| `VCE_PeachTree` | 5 | none | yes | UGA extension: peaches overwinter dormant; frost bud damage is not whole-tree death. |
| `VCE_PlumTree` | 5 | none | yes | UGA extension: plums behave similarly to peaches in dormancy/bloom damage. |
| `VCE_PearTree` | 5 | none | yes | Apple/pear temperature-driven dormancy research; VPE describes cool-climate pear. |
| `VCE_Opuntia` | 8 | -8 | no | VPE generic desert prickly pear, species unspecified; -8°C is moderate gameplay approximation, NOT an observed Opuntia lethal temperature. |
| `VCE_BearBerryBush` | 0 | -40 | no | UMN identifies northern bearberry Arctostaphylos uva-ursi as hardy broadleaf evergreen; keep leaves, use very low fallback cold death for game balance (not experimentally measured). |
| `VCE_BananaTree` | 15 | -2 | no | UF/IFAS: growth slows <16°C and freezes at <=0°C, <-2°C kills aboveground; game loses rhizome regrowth, so fixed death approximates plant loss. |

## Tradeoffs and required native checks
1. Grass and TallGrass use CCTO's generic perennials. Their VPE leafless art exists, but exact winter graphic/harvest behavior still requires loaded-game validation.
2. Apple/peach/plum/pear use **nonlethal cold dormancy**. Under the current shared CCTO implementation, extremely cold maps cannot kill those trees by cold alone. This is an existing abstraction; monitor gameplay implications before release.
3. Bearberry remains evergreen and is **not leafless** in winter; winter die-off near -40°C may affect naturally generated wild plants. VPE biome placement/native distribution must be sampled to verify it is not routinely erased.
4. Opuntia's species identity is ambiguous; future revision may choose a different balance once VPE growth biome distribution is sampled.
5. Banana is treated as killed at -2°C instead of resprouting from rhizome, because v1 explicitly changes **no VPE plant class**; this is an accepted v1 simplification to be reviewed in gameplay testing.
6. All death thresholds are strictly below growth minima. No VPE harvest, growth-days, yield, fertility, research, special plant classes, or MO/Vanilla CCTO values are changed.

**Evidence state:** engineering values sourced and reviewed for initial XML implementation; not a claim of native RimWorld PASS, tested wild-species survival, universal botanical thresholds, or author gameplay acceptance. Native verification stays HOLD pending the shared persistent host.
