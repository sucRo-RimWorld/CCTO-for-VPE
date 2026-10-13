# CCTO for VPE release gates

This is a development checklist, not evidence of release readiness.

- [ ] Project VE/non-VE implementation entry gate completed with verifiable owner decision record.
- [ ] Species-by-species numeric values, growth-vs-death/dormancy rationale reviewed for all 14 plant Defs.
- [ ] `Docs/PlantBalance.json` set to approved and `Scripts/build_vpe_patch.py` produces `Patches/ColdTolerance.xml`.
- [ ] Offline contract, exact VPE 1.6 source DefName + class audit, XPath matches and no duplicate CCTO extensions PASS.
- [ ] No change to six deferred custom-class plants and no change to CCTO Vanilla/MO values.
- [ ] Actual RimWorld 1.6 provider-loaded profiles, cold behavior boundaries and native ERROR 0 PASS on the shared host.
- [ ] Save/load, add/remove and plant survival tested; provider hashes, all tests and assumptions recorded.
- [ ] Subscriber payload inspected: no Docs/Scripts/Tests/assemblies or development assets.
- [ ] Workshop bilingual description, changelog and version synchronized only at approved release.
- [ ] Steam upload and downloaded subscriber payload separately verified; no claim from GitHub CI.
