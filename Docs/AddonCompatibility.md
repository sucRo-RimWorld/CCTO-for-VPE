# VPE addon family compatibility — owner procedure

**Authority:** `Docs/Design.md §8`; implementation tracking [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8). The candidate-only provider list is `Docs/AddonInventory.json`. **None of these addon packs has compatibility XML yet.**

## Architecture and scope

One independent **CCTO for VPE** Mod owns all selected cold-tolerance XML compatibility for the VPE plant ecosystem. Base CCTO owns the C# API and Vanilla/MO values. Optional VPE plant-pack support is not split into a new Workshop product or forced into CCTO base.

- **Existing v1:** `Patches/ColdTolerance.xml` / `Docs/PlantBalance.json` — only 14 ordinary VPE base plants; six custom-class plants deferred. Tests must continue to audit this exact scope, not an inflated total.
- **Subsequent optional packages:** `Patches/Addons/<Pack>.xml` and matching owner-approved per-pack balance/source file, only after full audit. No such runtime XML files exist in the current source.
- **Gating:** load/execute a pack's XML only if that pack's exact identity is found; use safe `PatchOperationFindMod` or a source-verified equivalent plus target existence checks. Each patch should be independent, including when two optional packs coexist. Confirm the exact match name, provider packageId (when supplied/verified), and current source Defs before coding. A missing provider must not produce a missing XPath error, silent data changes, or a new required dependency.
- **Startup size:** no C# or bundled DLL; no hard dependency on optional packs, no blanket XPath across other mods. Avoid needlessly scanning/updating unrelated XML on startup. Actual performance impact is **not measured**.
- **Behavioral scope:** native `plant/minGrowthTemperature` and CCTO extension only. No provider artwork, classes, fertility, harvest, growth days, new zones, research or cooking behavior copied/overridden.

## Candidate packs

| VPE upstream package | Inspection status | Notes |
|---|---|---|
| [More Plants](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants) | Repository 1.6 XML present; no compatibility implementation | Mixed standard/custom crop classes, fruit trees, cultivated flowers and special growing zones |
| [Mushrooms](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Mushrooms) | Repository 1.6 XML present; no compatibility implementation | Unusual fungal growth classes, possible conditional DLC content and at least one non-plant building |
| [Succulents](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Succulents) | Repository 1.6 XML present; no compatibility implementation | Decorative plants; foliage/evergreen hardiness requires individual balance |
| [Flowers](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Flowers) | Repository 1.6 XML present; no compatibility implementation | Decoratives and special bloom behavior; some parent-only ThingDefs |

These are verified repositories/candidate sets, **not supported-pack claims or verified package IDs**. Their About.xml may omit a top-level packageId; do not guess it. Future third-party **VPE plant** addons may be inventoried here if they genuinely provide plants; unrelated VE packs remain out of scope.

## Entry checklist per additional pack

1. Pin source/provider revisions, RimWorld version, hard dependencies and optional DLC. Inspect loaded/supported plant definitions, parent-only ThingDefs, duplicate DefNames, `thingClass` and interactions.
2. Classify every candidate: **ordinary XML-eligible**, **custom-class requires manual audit**, **non-plant/out-of-scope**. Do not implement special plants merely because a similar XML field exists.
3. Record crop-specific numeric evidence and parity with existing CCTO settings where the plant is equivalent; capture independently reviewable owner source.
4. Add a separate, conditional patch under `Patches/Addons/` with static checks for absent/present provider, one extension per included Def, safe XPath, no XML cross-effects when other packs are absent.
5. Preserve v1 14+6 tests and 7 shared counterparts. CI checks source/pack value parity as source evidence, not as native gameplay PASS. Publish exact supported-pack list and the unverified native-state disclosure.
6. Triage feedback from real VPE users in [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4); no mandatory author native-play test. Steam upload and payload verification remain author-controlled.
