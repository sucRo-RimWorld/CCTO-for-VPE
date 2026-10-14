# More Plants — RimWorld 1.6 preliminary source inventory (2026-10-15)

**State:** source XML catalog only; not an implemented/approved temperature patch, full gameplay-class audit, runtime test or supported Workshop feature.

- Provider: [Vanilla Plants Expanded - More Plants](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants), upstream `main` commit `a4afc14f54e84c623df3021781715a1f22f21e1d`.
- Verified upstream `About/About.xml` packageId: `VanillaExpanded.VPlantsEMore`; requires VPE, Vanilla Expanded Framework and Harmony.
- Upstream `loadFolders.xml` 1.6: unconditional root `/` plus `1.6`, with independent conditional 1.6 folders for `Ludeon.RimWorld.Ideology`, `VanillaExpanded.VCookE`, `OskarPotocki.VFE.Medieval2`.
- Upstream itself lists 1.7 and reuses its 1.6 directory in a `v1.7` load-folder stanza. **CCTO for VPE is still 1.6-only**; no 1.7 support declared here.
- This catalog counts concrete `ThingDef` declarations with `plant` nodes in these six source XML files. Parent/assembly behavior, optional provider combinations and inherited loaded defaults need later verification.

## Unconditional 1.6 source declarations — 43

**Farm, 26** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Farm.xml):

`VCE_Celery`, `VCE_Pineapple`, `VCE_Lettuce`, `VCE_BrusselsSprout`, `VCE_Cassava`, `VCE_SweetPotato`, `VCE_Radish`, `VCE_Buckwheat`, `VCE_Peanut`, `VCE_PeanutSecondary`, `VCE_Sunflower`, `VCE_Okra`, `VCE_Garlic`, `VCE_Carrot`, `VCE_Beans`, `VCE_Chickpea`, `VCE_BellPepper`, `VCE_YellowBellPepper`, `VCE_Taro`, `VCE_Watercress`, `VCE_Lotus`, `VCE_WaterChestnut`, `VCE_Melon`, `VCE_Cucumber`, `VCE_ButternutSquash`, `VCE_AloeVera`.

**Flowers, 12** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Flowers.xml):

`VCE_Canola`, `VCE_Lavender`, `VCE_FragrantbloomRose`, `VCE_Hyacinth`, `VCE_Jasmine`, `VCE_Lily`, `VCE_Orchid`, `VCE_Plumeria`, `VCE_Tulip`, `VCE_Vanilla`, `VCE_Violet`, `VCE_YlangYlang`.

**Trees, 5** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Tree.xml):

`VCE_TreeAvocado`, `VCE_TreeOlive`, `VCE_CoconutPalm`, `VCE_TreeAlmond`, `VCE_TreeMango`.

## Optional source declarations — 8

- Ideology **3** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Mods/Ideology/Defs/ThingDefs_Plants/Plants_Cultivated_Tunneller.xml): `VCE_Moss`, `VCE_Tinctshroom`, `VCE_Healshroom`.
- Vanilla Cooking Expanded **4** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Mods/VanillaCookingExpanded/Defs/ThingDefs_Plants/Plants_Cultivated_Farm_Cereals.xml): `VCE_Barley`, `VCE_Sorghum`, `VCE_Rye`, `VCE_Oats`.
- Vanilla Factions Expanded Medieval 2 **1** — [source](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants/blob/main/1.6/Mods/VanillaFactionsExpandedMedieval/Defs/ThingDefs_Plants/Plants_Cultivated_Farm_Vikings.xml): `VCE_Blueberry`.

## Explicit custom thingClass — 17 declarations requiring behavior audit

- Farm **13**: `Lettuce` (NeedsOutside), `BrusselsSprout` (AffectedBySnow), `Cassava` (AffectedByFog), `SweetPotato` (PrefersRockyAndNoFrost), `Peanut` (SowsAdjacent), `Sunflower` (FasterInTropics), `Okra` and `Garlic` (Resistant), `Carrot` and `Beans` (GrowsInTandem), `BellPepper` and `YellowBellPepper` (TransformOnMaturity), `WaterChestnut` (HighTempAffected).
- Trees **3**: `TreeOlive` (PrefersRocky), `CoconutPalm` (ChecksSea), `TreeAlmond` (WaterNearby).
- Conditional Medieval 2 **1**: `Blueberry` (BenefitsFromApiary).

Suffixes above abbreviate the **source-declared** namespaces `VEF.Plants.*`, `VanillaPlantsExpandedMorePlants.*`, or `VanillaPlantsExpanded.*`; see each linked XML for exact identity. Their interaction with CCTO native min-growth / Harmony hooks has **not** been individually verified.

## Implementation blockers and next checks

1. Trace each custom class's implementation (including inherited native growth behavior) before temperature XML; identify transform/spawned secondaries and skip unsafe plants explicitly rather than silently patching them.
2. Resolve `VCE_PeanutSecondary` and maturity-transformed peppers without producing duplicate extensions or introducing behavior changes.
3. Review aquatic/sandy cultivation, optional DLC/other-provider activated targets, and cross-mod collision/parity with CCTO and AMJ plants. In particular, do not assume the VPE Buckwheat and existing crops have equal species settings without a verified counterpart.
4. Establish audited per-plant `minGrowthTemperature`, `coldDeathTemperature` and/or `coldDormancy` in a separate More Plants balance source. Source XML catalog alone **does not approve 51 settings**.
5. Generate `Compatibility/MorePlants/Patches/ColdTolerance.xml` conditionally for verified provider `VanillaExpanded.VPlantsEMore` and separately guard conditional-provider Defs; preserve all base VPE 20 rules and nine parity tests, with absent/present provider static contracts and exact subscriber ZIP verification.
6. Keep user-waived native VPE tests distinct from mandatory static/package gates. No Workshop release is authorized by this inventory.
