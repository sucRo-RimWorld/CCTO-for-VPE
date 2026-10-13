# CCTO for VPE（CCTO VPE対応）

Independent optional XML compatibility addon for **Crop Cold Tolerance Overhaul** (CCTO) and **Vanilla Plants Expanded** (VPE).

**Validation policy:** Source XML for 14 VPE 1.6 plants is implemented and statically checked, but **it has not been independently tested in a running game**. The author does not play with VPE; issues will be addressed based on reports from users who do. Report reproducible errors or unexpected cold behavior through [GitHub Issues](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose). The addon has not been published to Steam by this repository change. Species model assumptions are documented in [TemperatureEvidence](Docs/Research/TemperatureEvidence.md).

- CCTO's Vanilla and Medieval Overhaul plant support stays in CCTO itself.
- V1 targets 14 ordinary VPE 1.6 plant definitions; six custom-class plants are deferred.
- This **same** Mod is the owner of future compatibility for optional VPE plant add-ons (More Plants, Mushrooms, Succulents, Flowers), but **none of those packs is supported by XML yet**. They will use independent, conditional XML only when installed; see [candidate inventory](Docs/AddonCompatibility.md).
- Initial per-species growth, cold-death and dormancy values are recorded in `Docs/PlantBalance.json`; `Patches/ColdTolerance.xml` is generated from them.
- The addon adds no C# or bundled DLL; it will use CCTO's existing XML extension.
- RimWorld 1.6 is the source-inspected target. No 1.7 VPE compatibility or native runtime PASS is claimed.

See [owner design](Docs/Design.md), [balance status](Docs/PlantBalance.json) and [active coordination](Docs/Coordination.md).

## 日本語

CCTOとVanilla Plants Expanded向けの独立した任意互換Mod。

**実ゲーム未検証。** VPE通常植物14種の耐寒性XMLを実装し、静的検証済み。作者はVPEを使用していないため、公開前の実機検証は必須とせず、利用者からの不具合報告をもとに修正する。症状・Mod構成・再現手順は [GitHub Issues](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose) に報告できる。数値はゲームバランス上の近似値。今回の変更はSteam公開を意味しない。

v1はVPE 1.6の通常植物14種を対象とし、独自植物クラス6種は別途検討する。MOの対応は分離せず、CCTO本体に残す。

**VPE系列の追加植物Modへの耐寒性互換も本Modで一元管理する。** More Plants・Mushrooms・Succulents・Flowersは今後の対応候補で、現在は未実装。追加Modを必須依存にせず、導入されている場合だけXMLを適用する。
