# CCTO for VPE release gates

This is a development checklist, not evidence of release readiness.

- [x] Owner VE/non-VE existing-Mod comparison and evidence-hashed decision record written; formal Project validator run remains separate.
- [x] Source-reviewed initial numeric values and botanical/gameplay rationales recorded for all 14 plants; author playtest judgment remains separate.
- [x] `Docs/PlantBalance.json` contains initial approved-for-implementation values; `Patches/ColdTolerance.xml` generated; static semantic validation added.
- [ ] Offline contract, exact VPE 1.6 source DefName + class audit, XPath matches and no duplicate CCTO extensions PASS.
- [ ] No change to six deferred custom-class plants and no change to CCTO Vanilla/MO values.
- [ ] Actual RimWorld 1.6 provider-loaded profiles, cold behavior boundaries and native ERROR 0 PASS on the shared host.
- [ ] Save/load, add/remove and plant survival tested; provider hashes, all tests and assumptions recorded.
- [ ] Subscriber payload inspected: no Docs/Scripts/Tests/assemblies or development assets.
- [ ] Workshop bilingual description, changelog and version synchronized only at approved release.
- [ ] Steam upload and downloaded subscriber payload separately verified; no claim from GitHub CI.
