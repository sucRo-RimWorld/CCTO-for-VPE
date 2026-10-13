# CCTO for VPE Agent Instructions

## Startup (required)
1. Read this file and `main:Docs/Coordination.md` first, including later corrections.
2. Read [Project AGENTS](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/AGENTS.md) and [SharedRules](https://github.com/sucRo-RimWorld/Ancient-Medieval-Japan-Project/blob/main/Docs/SharedRules.md); respect scope, prior-art gate, native-testing hold and PR-only GitHub writes.
3. Read `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/PriorArt.md` and CCTO's [Framework.md](https://github.com/sucRo-RimWorld/RimWorld-Crop-Cold-Tolerance-Overhaul/blob/main/Docs/Framework.md) before temperature XML implementation.

## Ownership
- This repo owns VPE-only cold-tolerance values, Def mappings, optional compatibility XML, packaging, its own documentation and tests. CCTO retains its C# framework and **all Vanilla/MO data**. MO separation is cancelled.
- Version 1: the 14 VPE 1.6 plants explicitly listed in `Docs/PlantBalance.json` with no custom `thingClass`. Six custom-class VPE plants are excluded pending individual investigation. Do not silently expand the set.
- Do not change VPE's plant classes, yield, fertility, harvest, recipes, graphics or growth days. Do not bundle other mods' assets or assemblies.
- `Docs/PlantBalance.json` is the reviewed implementation balance source; [TemperatureEvidence](Docs/Research/TemperatureEvidence.md) documents the botany-to-gameplay abstraction and [ImplementationDecision](Docs/Research/ImplementationDecision.json) owns the hashed VE/non-VE decision record. Never silently tune compiled XML instead of the balance source. All changes require source evidence, regeneration and static checks; native loaded-game behavior remains **unverified** unless directly evidenced; user bug reports are the adopted post-distribution validation route, not a substitute for evidence of a runtime PASS.
- The author does not use VPE and has explicitly waived mandatory pre-publication native RimWorld testing **for this optional addon only**. Require the owner static checks and packaging/public copy gates; disclose that native gameplay is unverified and handle reproducible player reports through issue #4. If an actual native test is later needed, use the shared persistent host; never bootstrap a chat-local game install or infer PASS from no reports.

## Integration and reports
- Changes use topic branches and PRs, never direct `main` edits. Keep `Docs/Coordination.md` authoritative on `main` only (PR integration may temporarily contain its pending change). Confirm exact PR checks before merge.
- Present **test premises and items** (14 included, six excluded, exact dependency IDs, field behavior, no duplicate extension, no code assembly), their results and remaining untested scenarios.
- Steam release and Workshop publication are author-controlled; never claim either from CI or a repository merge.
