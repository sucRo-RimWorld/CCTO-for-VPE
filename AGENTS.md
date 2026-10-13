# CCTO for VPE Agent Instructions

## Startup (required)
1. Read this file and `main:Docs/Coordination.md` first, including later corrections.
2. Read [Project AGENTS](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/AGENTS.md) and [SharedRules](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/SharedRules.md); respect scope, prior-art gate, native-testing hold and PR-only GitHub writes.
3. Read `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/PriorArt.md` and CCTO's [Framework.md](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Docs/Framework.md) before temperature XML implementation.

## Ownership
- This repo owns VPE-only cold-tolerance values, Def mappings, optional compatibility XML, packaging, its own documentation and tests. CCTO retains its C# framework and **all Vanilla/MO data**. MO separation is cancelled.
- Version 1: the 14 VPE 1.6 plants explicitly listed in `Docs/PlantBalance.json` with no custom `thingClass`. Six custom-class VPE plants are excluded pending individual investigation. Do not silently expand the set.
- Do not change VPE's plant classes, yield, fertility, harvest, recipes, graphics or growth days. Do not bundle other mods' assets or assemblies.
- `Docs/PlantBalance.json` is an unfinished data proposal, **not approved numeric balance**. Do not assign arbitrary values or create production `Patches/ColdTolerance.xml` until all 14 entries have reviewed values and the Project [Existing-Mod Audit](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/Research/ExistingModAudit.md) gate is complete.
- Runtime RimWorld testing uses the shared persistent-host route when available; do not recreate chat-local game installs. Static validation alone never proves loaded-game behavior.

## Integration and reports
- Changes use topic branches and PRs, never direct `main` edits. Keep `Docs/Coordination.md` authoritative on `main` only (PR integration may temporarily contain its pending change). Confirm exact PR checks before merge.
- Present **test premises and items** (14 included, six excluded, exact dependency IDs, field behavior, no duplicate extension, no code assembly), their results and remaining untested scenarios.
- Steam release and Workshop publication are author-controlled; never claim either from CI or a repository merge.
