# CCTO for VPE（CCTO VPE対応）

Independent optional XML compatibility addon for **Crop Cold Tolerance Overhaul** (CCTO) and **Vanilla Plants Expanded** (VPE).

**Development status:** repository initialized; temperature balance and runtime patch are not yet implemented. Installing this source checkout does not yet change VPE cold tolerance.

- CCTO's Vanilla and Medieval Overhaul plant support stays in CCTO itself.
- V1 targets 14 ordinary VPE 1.6 plant definitions; six custom-class plants are deferred.
- Final per-species minimum growth temperatures, cold-death thresholds and dormancy are pending.
- The addon adds no C# or bundled DLL; it will use CCTO's existing XML extension.
- RimWorld 1.6 is the source-inspected target. No 1.7 VPE compatibility or native runtime PASS is claimed.

See [owner design](Docs/Design.md), [balance status](Docs/PlantBalance.json) and [active coordination](Docs/Coordination.md).

## 日本語

CCTOとVanilla Plants Expanded向けの独立した任意互換Mod。

**開発中。** 現時点では温度設定・実行時XMLパッチは未実装で、このソースを導入しても植物の耐寒性は変更されない。

v1はVPE 1.6の通常植物14種を対象とし、独自植物クラス6種は別途検討する。MOの対応は分離せず、CCTO本体に残す。
