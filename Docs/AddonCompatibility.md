# VPE addon family compatibility — owner procedure

**Authority:** `Docs/Design.md §8`; implementation tracking [issue #8](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/8). `Docs/AddonInventory.json` is the candidate inventory. **No optional pack compatibility XML is implemented or shipped yet.**

## Current and future layout

The single CCTO for VPE addon owns the VPE core and eligible VPE plant-provider add-ons; CCTO base owns Vanilla/MO and the C# framework. Only VPE 1.6 is source-inspected.

- **Implemented core:** `Patches/ColdTolerance.xml` and `Docs/PlantBalance.json` cover exactly **20** base VPE plants (14 normal, six custom-class); no optional pack rows in this source.
- **Runtime loader:** `LoadFolders.xml` contains a `<v1.6>` stanza with `<li>/</li>`, which must remain unconditional to load core `Patches/`. No current candidate has an `IfModActive` entry.
- **Future pack XML:** `Compatibility/<Pack>/Patches/ColdTolerance.xml`, with separately audited owner-specific balance and tests. The `Compatibility/` directory does not exist until a pack has passed the audit.
- **Pack gate:** add one `<li IfModActive="EXACT_VERIFIED_PACKAGE_ID">Compatibility/<Pack></li>` inside `LoadFolders.xml` for each approved pack. Use the provider's real active Package ID from audited source/loaded metadata; do not infer it from a repository name or invent an ID where the upstream About.xml omits one. This keeps absent-pack XML out of RimWorld loading/parsing, rather than executing a no-op `PatchOperationFindMod` inside always-loaded XML.
- **Packaging:** `Scripts/build_release.py` explicitly includes `LoadFolders.xml` and rejects currently unsupported loader entries. Once a pack is implemented, update the exact ZIP allowlist, loader validation, and negative absent/present/provider-combination tests *in the same change*; verify the optional patch XML reaches the actual subscriber ZIP. The current eight-file release contains no pack XML.
- **Compatibility:** only CCTO and base VPE are hard dependencies. No addon C#/DLL or copied provider assets. No blanket XPath scans across other Mods. `PatchOperationFindMod` or target-existence guards may still be used as *secondary* safety checks after a pack's folder has been selected.
- **Performance:** the purpose of conditional folders is to avoid parsing patches belonging to absent providers. No actual startup time measurement or loaded-game PASS exists for this design.

## Candidate packs (unsupported)

| VPE upstream package | Inspection status | Notes |
|---|---|---|
| [More Plants](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-MorePlants) | Repository 1.6 XML present; no compatibility implementation | Mixed normal/custom plant classes, fruit trees and special growing zones |
| [Mushrooms](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Mushrooms) | Repository 1.6 XML present; no compatibility implementation | Custom fungal growth and possibly DLC-gated content; exclude non-plant buildings |
| [Succulents](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Succulents) | Repository 1.6 XML present; no compatibility implementation | Decorative plants; requires individual temperature/dormancy evidence |
| [Flowers](https://github.com/Vanilla-Expanded/VanillaPlantsExpanded-Flowers) | Repository 1.6 XML present; no compatibility implementation | Some parent-only Defs and special bloom behavior |

These are candidates, **not** verified Package IDs or supported content. Additional third-party VPE plant packs require the same review.

## Per-pack implementation gate

1. Pin upstream provider source/commit, 1.6 compatible XML, actual Package ID, dependency/DLC conditions, all eligible PlantDefs, parent-only placeholders and duplicate names.
2. Review ordinary and custom `thingClass` separately, including game code behavior; defer any unsafe class or special mechanics instead of guessing.
3. Record each approved minimum growth, cold-death or dormancy value and CCTO Vanilla/MO shared-species parity evidence outside the base 20-plant balance source.
4. Generate pack XML inside its isolated `Compatibility/<Pack>/Patches/`, add only its audited `IfModActive` loader entry, package it in the subscriber ZIP, and reject absent-provider patches, XPath failures, double extensions, and interference across concurrently installed packs in static tests.
5. Keep existing 20-core/six-custom-class/nine-shared-counterpart tests and hard dependencies intact. Distinguish offline packaging validation from loaded-game testing; the author waives mandatory native VPE tests only for this optional addon.
6. Update accurate supported-pack disclosure before a separate author-controlled Workshop action; route user bug reports through [issue #4](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/4).
