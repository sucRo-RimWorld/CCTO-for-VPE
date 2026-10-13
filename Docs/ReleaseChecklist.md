# CCTO for VPE — release and community verification checklist

**Policy (2026-10-13):** The author does not use VPE. **Native RimWorld test execution is NOT a pre-release gate** for this optional XML addon. After distribution, actual VPE users' bug reports are the chosen diagnostic route. This exception is not a runtime PASS and does not apply to CCTO base/MO or other AMJ releases.

## Source gates — keep mandatory

- [x] VE/non-VE existing-Mod comparison and hashed implementation-decision record created. The standalone Project audit validator has not been run separately; owner tests inspect decision structure/hashes.
- [x] Initial 14-species numeric balance, rationale and generated `Patches/ColdTolerance.xml` committed. Values are model assumptions, not universal measured plant death limits.
- [x] CI asserts 14 included Defs / six excluded special-class Defs, metadata and XML values, no addon C# or bundled DLL, and 7 CCTO Vanilla/MO counterpart values from current CCTO `main`.
- [ ] Confirm these source/CI gates again against the exact candidate to be published. Mark any missing or failed check as a release blocker.
- [ ] Verify VPE 1.6 source/Def identity still matches the supported version. **Do not imply RimWorld 1.7 VPE support.**

## Actual distribution gates — author controlled

- [ ] Inspect the exact subscriber package: `About/About.xml`, `Patches/ColdTolerance.xml`, required identity/attribution only; no `Docs/`, `Scripts/`, `Tests/`, local test checkouts or DLLs.
- [ ] English and Japanese public descriptions explicitly state: **not independently tested in a running game; user bug reports welcomed**. Include the [bug-report link](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose).
- [ ] Obtain author publication decision; align version/changelog/Workshop description if publishing. This GitHub change **does not upload** anything to Steam.
- [ ] After manual Steam upload, independently verify the actual published subscriber payload; do not infer upload/download success from source CI.

## Post-distribution (not a prerequisite to source integration)

- [ ] Accept and triage reports using the bilingual issue template or Workshop comments; capture applicable versions, exact plant, temperature/season, reproduction steps, error log and Mod list, if available.
- [ ] Investigate reported breaks, update canonical values/code via scoped PR and rerun applicable static gates. Seek reporter confirmation if practical; no report does not mean PASS.
- [ ] Consider targeted native testing on the shared host only for difficult bugs when it becomes available. Do not require author native gameplay tests as a publication prerequisite.
- [ ] Review compatibility with a future VPE 1.7 build separately before claiming it.

Bug-report and feedback workflow: [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4). No native tests, save compatibility tests, or Workshop distribution have been demonstrated by CI.
