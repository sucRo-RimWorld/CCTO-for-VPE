# CCTO for VPE — release and community verification checklist

**Policy (2026-10-13):** The author does not use VPE. **Native RimWorld test execution is NOT a pre-release gate** for this optional XML addon. After distribution, actual VPE users' bug reports are the chosen diagnostic route. This exception is not a runtime PASS and does not apply to CCTO base/MO or other AMJ releases.

## Source gates — keep mandatory

- [x] VE/non-VE existing-Mod comparison and hashed implementation-decision record created. The standalone Project audit validator has not been run separately; owner tests inspect decision structure/hashes.
- [x] Original 14-species balance plus six custom-class numeric profiles, rationale and generated `Patches/ColdTolerance.xml` committed. Values are model assumptions, not universal measured plant death limits.
- [x] CI asserts 20 included core Defs / six preserved custom-class identities / zero exclusions, metadata and XML values, no addon C# or bundled DLL, and 9 CCTO Vanilla/MO counterpart values from current CCTO `main`.
- [x] Source/CI verified for the reviewed 0.1.0 PR candidate, including the strict 20-Def XML/value contracts and 9 CCTO pairwise parity checks. After any later source edit, rerun on that exact revision before upload.
- [x] Public drafts name **only 20 VPE core plants** as implemented and exclude all optional VPE packs. The optional packs (More Plants, Mushrooms, Succulents, Flowers) stay unsupported until implemented.
- [x] VPE upstream `main` at `6823417d3aa206880a8cc9fe7c2239f3cb66a78b` has all 20 matching DefNames in `1.6/Defs/ThingDefs_Plants/Plants_Cultivated_Farm.xml` and `Plants_Cultivated_Trees.xml`; all six custom-class identities also match. This is **source inspection, not loaded-game testing**. Beet winter growth and cherry winter blossoms remain noted caveats; do not imply VPE 1.7 support.

## Actual distribution gates — author controlled

- [x] PR #14 candidate ZIP is produced by `Scripts/build_release.py` and checked by `Tests/test_release_candidate.py`: exactly `About/About.xml`, `About/Manifest.xml`, `About/Changelog.txt`, `About/Preview.png`, `Patches/ColdTolerance.xml`, `LICENSE`. No `Docs/`, `Scripts/`, `Tests/`, copied provider DLL or child-pack XML. Both source and preview PNG SHA-256 match the author-approved `Docs/ApprovedPreview.json`.
- [ ] Before publishing, verify the final installed Mod folder used by the Steam publisher contains the same six reviewed subscriber files (including the approved preview). Check after any copying/deployment changes.
- [x] Prepared English/Japanese Workshop and Japanese 2game descriptions explicitly state: **not independently tested in a running game; user bug reports welcomed**. Include the [bug-report link](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose).
- [x] Initial 0.1.0 About/Manifest/Changelog source synchronized; Workshop and 2game EN/JA drafts, including save uncertainty, prepared. Author-controlled Steam upload/visibility and 2game site posting remain unperformed. **A passing source/ZIP CI does not mean the Mod is distributed.**
- [ ] After manual Steam upload, independently verify the actual published subscriber payload; do not infer upload/download success from source CI.

## Post-distribution (not a prerequisite to source integration)

- [ ] Accept and triage reports using the bilingual issue template or Workshop comments; capture applicable versions, exact plant, temperature/season, reproduction steps, error log and Mod list, if available.
- [ ] Investigate reported breaks, update canonical values/code via scoped PR and rerun applicable static gates. Seek reporter confirmation if practical; no report does not mean PASS.
- [ ] Consider targeted native testing on the shared host only for difficult bugs when it becomes available. Do not require author native gameplay tests as a publication prerequisite.
- [ ] Review compatibility with a future VPE 1.7 build separately before claiming it.

**CI verification:** [release-preparation PR #14](https://github.com/sucRo-RimWorld/CCTO-for-VPE/pull/14). CI must pass again for any changed PR head and for the merge-commit on main; the release artifact is a candidate, not an uploaded subscriber proof.

Bug-report and feedback workflow: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4). No native tests, save compatibility tests, or Workshop distribution have been demonstrated by CI.
