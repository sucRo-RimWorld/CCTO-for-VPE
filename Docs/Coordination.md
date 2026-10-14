# CCTO for VPE Coordination — main only

This file is for cross-workstream state and handoffs only. Values, behavior and release policy are authoritative in `Docs/Design.md`, `Docs/PlantBalance.json`, `Docs/Research/TemperatureEvidence.md`, `Docs/ReleaseChecklist.md`, and `Patches/ColdTolerance.xml`.

## VPE-COMMUNITY-VALIDATION-20261013

**Owner:** CCTO for VPE.
**Status:** VPE 1.6 CORE 20 XML IMPLEMENTED; 0.1.0 SOURCE/PACKAGE/APPROVED PREVIEW MERGED VIA [PR #13](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/13); MAIN SOURCE/ZIP CI PASS; **NATIVE GAMEPLAY NOT RUN; USER BUG REPORTS ADOPTED**. Author Workshop release has not been performed.

- Author explicitly does not use VPE. For CCTO for VPE **only**, mandatory pre-release native RimWorld testing is waived. After users try the addon, bugs and compatibility issues will be handled through the repository [issue tracker](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues), with a bilingual report template; [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4) owns follow-up. No reports is not native PASS.
- Source-release preparation completed in merged PR #13: exact reviewed 20-plant and nine-parity tests; VPE source DefName/class comparison at upstream commit `6823417d3aa206880a8cc9fe7c2239f3cb66a78b`; bilingual Workshop + 2game copy; 0.1.0 About/Manifest/Changelog; approved preview and source PNG with hash assertions; six-file subscriber-only ZIP with offline test and CI artifact. Author still must verify the actual installed upload source and publish/inspect the downloaded Steam item. No VPE 1.7 compatibility or native game PASS asserted.
- CCTO keeps the Vanilla + Medieval Overhaul mappings/framework. No numeric, runtime XML or dependency change is authorized by this reporting-policy change.
- Shared persistent host remains the project direction for any *optional* later VPE native reproduction, not an unresolved release prerequisite for this addon.

## VPE-ADDON-OWNERSHIP-20261013

**Owner:** CCTO for VPE (single compatibility addon for the VPE plant-provider ecosystem).
**Status:** AUTHOR APPROVED SINGLE OWNER; FOUR UPSTREAM VPE CHILD PACKS INVENTORIED AS **UNSUPPORTED CANDIDATES**; implementation of additional patch XML OPEN in [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8).

- The original 14+6 VPE v1 inventory has been expanded to 20 included / 0 excluded base VPE 1.6 Defs, with nine CCTO counterpart parity checks. No new temperature XML, new package dependencies or native tests in this decision.
- Four detected modules: More Plants, Mushrooms, Succulents, Flowers (source revisions recorded in `Docs/AddonInventory.json`); confirm exact provider identity and custom/ordinary classes before each conditional patch. CCTO base is **not** the owner of VPE family addon definitions.
- Community bug reports/optional native reproduction remain with issue #4; do not treat VPE game tests as a publication prerequisite. Design/source-of-truth: `Docs/Design.md §8`, `Docs/AddonCompatibility.md`.

## VPE-SIX-CUSTOM-CLASS-SOURCE-AUDIT-20261013

**Owner:** CCTO for VPE original VPE v1 plant scope.
**Status:** SOURCE INSPECTION COMPLETE — **6/6 native growth-minimum + CCTO cold-death extension XML-ADDRESSABLE**, SIX EXTRA CUSTOM-CLASS PLANTS NOW SOURCE-IMPLEMENTED WITH ENGINEERING VALUES; NATIVE GAMEPLAY UNVERIFIED.

Verified VPE 1.6 custom class methods, RimWorld 1.6 Plant.TickLong and PlantUtility.GrowthSeasonNow, and CCTO's base Plant Harmony hooks. Eggplant/Beet retain hardcoded growth multipliers; Beet's documented 10% out-of-season growth-rate return is blocked by base TickLong actual growth gating; Cherry winter blossom graphics override leafless priority. VPE special behavior remains unchanged; CCTO compatibility source values are in `Docs/PlantBalance.json` and `Docs/Research/SixCustomClassBalance.md`. Exact class evidence and limitations in `Docs/Research/VpeCustomPlantClassAudit.md`, completed source XML implementation in [issue #10](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/10). No actual loaded-game testing or steam distribution performed.

## VPE-CUSTOM-SIX-XML-INTEGRATION-20261013

**Owner:** CCTO for VPE core PlantDefs. **Status:** SOURCE XML FOR 20 VPE BASE PLANTS; 6/6 PREVIOUSLY DEFERRED CLASS TARGETS NOW INCLUDED; CCTO PARITY EXPANDED TO 9; NATIVE GAMEPLAY UNVERIFIED.

PlantBalance.json owns added numerical decisions; [SixCustomClassBalance](Research/SixCustomClassBalance.md) owns six-class justification. Generator and static suite now validate 20 core XML targets and preserved `thingClass` identities without adding C#. CCTO base Vanilla/MO remains untouched; optional More Plants/Mushrooms/Succulents/Flowers are still only candidate packs in issue #8. Native testing remains waived by author and bug reporting #4. No Steam publication performed.

## VPE-STEAMCMD-PRIVATE-PUBLISHER-20261013

**Owner:** CCTO for VPE publishing (separate from native RimWorld test-host infrastructure).
**Status:** FIRST PRIVATE UPLOAD SUCCESS; AUTHOR-CONFIRMED PRIVATE VISIBILITY; DESCRIPTION LF AND FULL CHANGE-NOTE SOURCE FIXES MERGED; LIVE METADATA/TAGS AND SUBSCRIBER PAYLOAD UNVERIFIED.

The author accepted ChatGPT→GitHub Actions→isolated self-hosted SteamCMD as an optional path for **creating/updating a private Workshop item only**. Manual `workflow_dispatch` `preflight` runs source tests/payload verification without Steam; `upload_private` is guarded by exact `main` SHA and `PRIVATE_ONLY`, and requires dedicated runner label `steamcmd-private-publisher` and locally managed Steam session. AppID 294100, visibility `2`, persistent local PublishedFileId, no GitHub credentials, and no automatic public transition are enforced by `Scripts/steamcmd_private.py` and `.github/workflows/steam-private.yml`. Author must later provision host, perform first private upload and verify actual item visibility and subscriber ZIP. Formal owner runbook: `Docs/SteamCMDPrivatePublishing.md`; [ReleaseChecklist](ReleaseChecklist.md). Does not remove author waiver of optional VPE native-game tests or authorize other AMJ publisher deployments.

2026-10-14: author confirmed private upload and private visibility, but reported literal `\\n` in the description. VDF serialization correction and bilingual six-custom-plant risk disclosure are prepared; actual corrected Steam description and downloaded payload remain pending. Formal procedure: `Docs/SteamCMDPrivatePublishing.md`. Intermittent GitHub DNS failures remain unresolved.

2026-10-14 Workshop metadata handoff: [PR #22](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/22) merged as `6fec0aeaf034af1e93a901175948202909f2f0ae` with offline contract CI PASS. Its SteamCMD VDF now contains the **complete current-version bilingual changenote**, not just the version heading; the expected `Mod` / `1.6` category tags are derived from About.xml and surfaced in preflight. **Neither change is proof of live Steam reflection.** SteamCMD does not reliably write category tags, so an authenticated Steamworks metadata route + private-item read-back is OPEN in [issue #23](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/23), separate from SteamCMD host provisioning [issue #17](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/17). No automatic public upload, extra supported game version, native-game PASS, verified change-history display or subscriber read-back is authorized/claimed. Canonical implementation and procedure: `Scripts/steamcmd_private.py`, `Docs/SteamCMDPrivatePublishing.md`.

2026-10-14 Workshop identity correction (author-reported): CCTO for VPE's **currently retained** Workshop item is https://steamcommunity.com/sharedfiles/filedetails/?id=3819497323. A YADA attempt created a separate item; do not assume which item was the duplicate or delete any Steam listing without a creator-side audit. The owner source now pins `About/PublishedFileId.txt` to `3819497323`, packs and validates seven subscriber files, and rejects SteamCMD host state pointing to another item or `create_new_item=true`. **The existing host state and installed YADA folder have not been read or changed; no live Steam update, private visibility re-verification, tag sync or change-note read-back has been performed.** Canonical source/runbook: `About/PublishedFileId.txt`, `Scripts/build_release.py`, `Scripts/steamcmd_private.py`, `Docs/SteamCMDPrivatePublishing.md`; follow-up publishing infrastructure in issues #17 and #23.


2026-10-14 Steamworks tag-sync workstream (latest): `sync_tags_private`
and automatic post-`upload_private` Steamworks tagging target only the
author's existing Workshop ID `3819497323`. Windows-side interactive
Steamworks host is still **NOT PROVISIONED/VERIFIED** and is separate
from the functioning WSL SteamCMD publisher and the paused AMJ native
test host. A source-only `Prepare-WindowsSteamworksTagRunner.ps1`
launcher now pins/builds the reviewed upstream agent and runs the
non-mutating Steamworks desktop probe; GitHub Actions
`tag_runner_check` checks that exact session without modifying Steam.
Tags are derived from actual About versions (currently `Mod` + `1.6`).
Each *successful content upload* has a distinct no-replay tag sync
receipt keyed by GitHub run ID, and ambiguous `PENDING` aborts retry.
These are **source and offline-test results only**: no Windows host action,
Steamworks tag update, Steam page read-back, Steam change-note display
or subscriber verification has occurred. Formal source
`Scripts/steamworks_tags.py`, `Scripts/Prepare-WindowsSteamworksTagRunner.ps1`,
`Docs/SteamCMDPrivatePublishing.md`; follow-up issue #23.

2026-10-14 publisher route decision (latest author correction): YADA was
used to apply the latest CCTO for VPE Workshop update and the author reports
its tags reflected on the retained item `3819497323`. The author explicitly
will **not use YADA for future uploads**. Future uploads must use the
source-pinned private GitHub Actions `preflight` → WSL SteamCMD
`upload_private` → Windows Steamworks `sync_tags` route. **Do not send a
redundant tag update now** merely because the tag runner was registered.
The new Windows Steamworks runner was author-reported started, and local
Steamworks script probing reached runner launch, but GitHub Actions
`tag_runner_check` has NOT been run/evidenced. WSL publisher-host
state reconciliation and real end-to-end future upload remain pending.
Canonical operational source `Docs/SteamCMDPrivatePublishing.md`;
open deployment checks issue #23.
