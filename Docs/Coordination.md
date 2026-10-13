# CCTO for VPE Coordination — main only

This file is exclusively a cross-workstream status/handoff surface. Confirmed specifications and values are in `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/TemperatureEvidence.md` and `Patches/ColdTolerance.xml`, not here.

## VPE-RUNTIME-ACCEPTANCE-20261013

**Owner:** CCTO for VPE for actual VPE-specific behavior; shared persistent native host for execution.
**Status:** V1 XML SOURCE MERGED IN PR #3 (`235663629fc77e689f2292292ff4bd327b8bb5fa`); OFFLINE PR/MAIN CI PASS; NATIVE RIMWORLD/STEAM RELEASE UNVERIFIED.

- v1 covers precisely 14 VPE 1.6 ordinary-class PlantDefs, excludes six VPE custom-class plants. CCTO retains all Vanilla/MO data and C# framework; MO separation remains cancelled.
- Values are engineer-reviewed **gameplay model approximations**, not author playtest acceptance or experimentally proven lethal thresholds. Evidence and explicit limitations live in the owner research.
- **Native testing pending:** real Harmony/VEF/VPE/CCTO provider identity, Def load and extension uniqueness, cold boundary temperatures, dormancy/leafless rendering, fruit-tree overwintering, wild-plant seasonal dieoff, actual save add/remove/reload, MO optional-profile interaction, complete ERROR=0 logs. The Project shared persistent-host construction/testing remains on hold.
- **Publication pending:** output filtering and distributed Workshop payload, compatibility with RimWorld 1.7 VPE, and manual Steam upload. GitHub static checks do not prove these.
- Bootstrap + v1 source implementation completed in [PR #2](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/2) and [PR #3](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/3); initial implementation [issue #1](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/1) is closed. Remaining native + release acceptance belongs to [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).
