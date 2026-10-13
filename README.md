# CCTO for VPE（CCTO VPE対応）

Independent optional XML compatibility addon for **Crop Cold Tolerance Overhaul** (CCTO) and **Vanilla Plants Expanded** (VPE).

**Development status:** XML cold-tolerance patches have been implemented for 14 VPE 1.6 PlantDefs, but **the loaded-game behavior has not been validated or released**. All per-species model choices and limitations are documented in [TemperatureEvidence](Docs/Research/TemperatureEvidence.md).

- CCTO's Vanilla and Medieval Overhaul plant support stays in CCTO itself.
- V1 targets 14 ordinary VPE 1.6 plant definitions; six custom-class plants are deferred.
- Initial per-species growth, cold-death and dormancy values are recorded in `Docs/PlantBalance.json`; `Patches/ColdTolerance.xml` is generated from them.
- The addon adds no C# or bundled DLL; it will use CCTO's existing XML extension.
- RimWorld 1.6 is the source-inspected target. No 1.7 VPE compatibility or native runtime PASS is claimed.

See [owner design](Docs/Design.md), [balance status](Docs/PlantBalance.json) and [active coordination](Docs/Coordination.md).

## 日本語

CCTOとVanilla Plants Expanded向けの独立した任意互換Mod。

**開発中。** 通常植物14種の耐寒性XMLは実装済み。ただしRimWorldでのロード・挙動検証と配布は未実施。数値は植物ごとのゲームバランス上の近似値。

v1はVPE 1.6の通常植物14種を対象とし、独自植物クラス6種は別途検討する。MOの対応は分離せず、CCTO本体に残す。
