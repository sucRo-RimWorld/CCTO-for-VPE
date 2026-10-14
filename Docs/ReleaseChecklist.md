# CCTO for VPE — release and community verification checklist

**Policy (2026-10-13):** The author does not use VPE. **Native RimWorld test execution is NOT a pre-release gate** for this optional XML addon. After distribution, actual VPE users' bug reports are the chosen diagnostic route. This exception is not a runtime PASS and does not apply to CCTO base/MO or other AMJ releases.

## Source gates — keep mandatory

- [x] VE/non-VE existing-Mod comparison and hashed implementation-decision record created. The standalone Project audit validator has not been run separately; owner tests inspect decision structure/hashes.
- [x] Original 14-species balance plus six custom-class numeric profiles, rationale and generated `Patches/ColdTolerance.xml` committed. Values are model assumptions, not universal measured plant death limits.
- [x] CI asserts 20 included core Defs / six preserved custom-class identities / zero exclusions, metadata and XML values, no addon C# or bundled DLL, and 9 CCTO Vanilla/MO counterpart values from current CCTO `main`.
- [x] Source/CI verified for merged 0.1.0 candidate on main commit `75233eaef36dbac6544b855b9dececd14284b19c`, including the strict 20-Def XML/value contracts and 9 CCTO pairwise parity checks. After any later source edit, rerun on that exact revision before upload.
- [x] Public drafts name **only 20 VPE core plants** as implemented and exclude all optional VPE packs. The optional packs (More Plants, Mushrooms, Succulents, Flowers) stay unsupported until implemented.
- [x] VPE upstream `main` at `6823417d3aa206880a8cc9fe7c2239f3cb66a78b` has all 20 matching DefNames in `1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Farm.xml` and `Plants_Cultivated_Trees.xml`; all six custom-class identities also match. This is **source inspection, not loaded-game testing**. Beet winter growth and cherry winter blossoms remain noted caveats; do not imply VPE 1.7 support.

## Optional author-private SteamCMD route

- [x] A GitHub manual-only SteamCMD `preflight`/conditional `upload_private` workflow is implemented for **CCTO for VPE only**. The uploader hardcodes AppID `294100`, visibility `2` (creator-only), source/payload byte matching, existing-ID persistence and refusal of unconfirmed new item creation. See [SteamCMDPrivatePublishing](SteamCMDPrivatePublishing.md). Source-level tests use a mock SteamCMD, not real Steam.
- [ ] Provision/verify a **dedicated publisher** self-hosted runner with label `steamcmd-private-publisher`, secure local SteamCMD installation and separately authenticated Steam account; configure `steam-workshop-private` GitHub environment/review protections. This is independent of the Project native RimWorld testing host. No password, Steam Guard code or Steam token may be stored in GitHub.
- [ ] Run a **manual** `preflight` against an exact current main commit; only then, with private author authorization, run `upload_private` (first item requires `create_new_item=true` and `PRIVATE_ONLY`; updates require the saved ID and private verification).
- [ ] Confirm successful SteamCMD creation/update, preserve real PublishedFileId in the isolated runner, and **verify as creator** that the Workshop item is actually private and the subscribed payload matches the six authorized files. CI/SteamCMD success alone does not prove visibility or subscriber content.
- [ ] Keep the actual item private until the author separately directs any public switch. No automated public upload or publicity transition is implemented.

## Actual distribution gates — author controlled

- [x] PR #13 merged release candidate ZIP is produced by `Scripts/build_release.py` and checked by `Tests/test_release_candidate.py`: exactly `About/About.xml`, `About/Manifest.xml`, `About/Changelog.txt`, `About/Preview.png`, `Patches/ColdTolerance.xml`, `LICENSE`. No `Docs/`, `Scripts/`, `Tests/`, copied provider DLL or child-pack XML. Both source and preview PNG SHA-256 match the author-approved `Docs/ApprovedPreview.json`.
- [ ] Before publishing, verify the final installed Mod folder used by the Steam publisher contains the same six reviewed subscriber files (including the approved preview). Check after any copying/deployment changes.
- [x] Prepared English/Japanese Workshop and Japanese 2game descriptions explicitly state: **not independently tested in a running game; user bug reports welcomed**. Include the [bug-report link](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose).
- [x] Initial 0.1.0 About/Manifest/Changelog source synchronized; Workshop and 2game EN/JA drafts, including save uncertainty, prepared. Author-controlled Steam upload/visibility and 2game site posting remain unperformed. **A passing source/ZIP CI does not mean the Mod is distributed.**
- [ ] After manual Steam upload, independently verify the actual published subscriber payload; do not infer upload/download success from source CI.

## Post-distribution (not a prerequisite to source integration)

- [ ] Accept and triage reports using the bilingual issue template or Workshop comments; capture applicable versions, exact plant, temperature/season, reproduction steps, error log and Mod list, if available.
- [ ] Investigate reported breaks, update canonical values/code via scoped PR and rerun applicable static gates. Seek reporter confirmation if practical; no report does not mean PASS.
- [ ] Consider targeted native testing on the shared host only for difficult bugs when it becomes available. Do not require author native gameplay tests as a publication prerequisite.
- [ ] Review compatibility with a future VPE 1.7 build separately before claiming it.

**CI verification:** [release-preparation PR #13](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/13). CI must pass again for any changed PR head and for the merge-commit on main; the release artifact is a candidate, not an uploaded subscriber proof.

Bug-report and feedback workflow: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4). No native tests, save compatibility tests, or Workshop distribution have been demonstrated by CI.

## Existing Workshop identity lock (2026-10-14)

- [x] Author designated `3819497323` as the currently retained CCTO for
  VPE Workshop item after a YADA upload created a distinct item. The other
  item's identity, historical state and cleanup are not assumed.
- [x] `About/PublishedFileId.txt` is included and validated in the **current
  seven-file** source release; SteamCMD rejects mismatching host state and
  new-item creation. Earlier six-file evidence above is historical.
- [x] Author confirms YADA was used for the latest upload only, with
  version tags reflected; **YADA is retired for future publishing**. No
  future local-YADA deployment synchronization is required.
- [ ] For future GitHub Actions updates, verify the actual WSL SteamCMD
  publisher state `CCTO_STEAM_STATE` identifies `3819497323`, and verify
  creator ownership and private visibility before uploading.
- [ ] Independently reconcile `CCTO_STEAM_STATE` with the target Workshop
  item, owner and creator-private visibility before future SteamCMD updates.
- [ ] Verify the actual Steam page, tags, change notes, and subscriber payload
  on the selected item before claiming distribution consistency.


## Steamworks category-tag synchronizer — 2026-10-14

- [x] Owner source implements manual tag-only `sync_tags_private` and
  post-success `upload_private` metadata sync, on a separate Windows
  interactive Steamworks runner. It extracts category versions from the
  current `About.xml` and pins Workshop ID `3819497323`.
- [x] Offline test contract requires exact ID, `Mod`/approved versions,
  app ID 294100, logged-on Steamworks probe, no implicit creation/public
  visibility change, local `PENDING` submission intent, and no repeat
  submission after a local successful receipt.
- [x] Windows PowerShell 7 host launcher added for pinned upstream agent build,
  RimWorld Steam API discovery, Steam-session-only probe and interactive
  GitHub runner startup; source/tests only, no host execution yet.
- [x] Nonpublishing `tag_runner_check` manual action added. Post-upload tag
  refresh now tracks the successful GitHub workflow run ID, preventing an
  earlier successful tag-only receipt from suppressing a new upload refresh.
- [ ] Provision a dedicated Windows interactive desktop-Steam runner,
  pinned reviewed SteamWorkshopAgent build, Steam-native DLL override,
  user-private receipt path and actual Steam session.
- [ ] Run `tag_runner_check` against the exact main SHA from the logged-in
  Steam Windows session; record probe status and native-library fingerprint.
- [ ] Verify on the private Steam item that `SetItemTags` succeeded and
  current tags are visible; local callback success is not remote read-back.
- [ ] After a real SteamCMD update, verify both the complete changenote
  history and the tag job completed, with subscriber files unchanged.
