# CCTO for VPE Coordination — main only

This file is exclusively a cross-workstream status/handoff surface. Confirmed specifications and values are in `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/TemperatureEvidence.md` and `Patches/ColdTolerance.xml`, not here.

## VPE-RUNTIME-ACCEPTANCE-20261013

**Owner:** CCTO for VPE for actual VPE-specific behavior; shared persistent native host for execution.
**Status:** 14-PLANT XML SOURCE IMPLEMENTED AND OFFLINE CONTRACT PREPARED; NATIVE RIMWORLD/STEAM RELEASE UNVERIFIED.

- v1 covers precisely 14 VPE 1.6 ordinary-class PlantDefs, excludes six VPE custom-class plants. CCTO retains all Vanilla/MO data and C# framework; MO separation remains cancelled.
- Values are engineer-reviewed **gameplay model approximations**, not author playtest acceptance or experimentally proven lethal thresholds. Evidence and explicit limitations live in the owner research.
- **Native testing pending:** real Harmony/VEF/VPE/CCTO provider identity, Def load and extension uniqueness, cold boundary temperatures, dormancy/leafless rendering, fruit-tree overwintering, wild-plant seasonal dieoff, actual save add/remove/reload, MO optional-profile interaction, complete ERROR=0 logs. The Project shared persistent-host construction/testing remains on hold.
- **Publication pending:** output filtering and distributed Workshop payload, compatibility with RimWorld 1.7 VPE, and manual Steam upload. GitHub static checks do not prove these.
- Issue [#1](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/1) tracks remaining native/release acceptance.
