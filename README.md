# CCTO for VPE（CCTO VPE対応）

Independent optional XML compatibility addon for **Crop Cold Tolerance Overhaul** (CCTO) and **Vanilla Plants Expanded** (VPE).

**Release-source status:** Version 0.1.0 provides source XML for 20 VPE 1.6 core plants with passing static tests, but **it has not been independently tested in a running game**. The author does not play with VPE; issues will be addressed based on reports from users who do. Report reproducible errors or unexpected cold behavior through [GitHub Issues](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose). An existing Steam Workshop item, [3819497323](https://steamcommunity.com/sharedfiles/filedetails/?id=3819497323), has been confirmed by the author and Steam item-details API as **public**. This does not prove that the downloaded subscriber payload matches the current GitHub source; that verification remains open. Future uploads are separately author-authorized updates to this same item, not new-item creation or a privacy change. Species model assumptions are documented in [original 14-species evidence](Docs/Research/TemperatureEvidence.md) and [six custom-class balance](Docs/Research/SixCustomClassBalance.md).

- CCTO's Vanilla and Medieval Overhaul plant support stays in CCTO itself.
- VPE core 1.6 support now covers 20 source-implemented PlantDefs (14 ordinary plus six VPE custom-class targets) via XML, without changing custom classes. Runtime effects are not independently validated.
- This **same** Mod is the owner of future compatibility for optional VPE plant add-ons (More Plants, Mushrooms, Succulents, Flowers), but **none of those packs is supported by XML yet**. Once reviewed, each pack will use a separate `Compatibility/<Pack>/Patches/` folder selected through `LoadFolders.xml` and its verified `IfModActive` provider Package ID. Absent-pack XML will not be loaded. Currently the loader contains only the VPE 1.6 core path and no pack XML ships; see [candidate inventory](Docs/AddonCompatibility.md).
- Initial per-species growth, cold-death and dormancy values are recorded in `Docs/PlantBalance.json`; `Patches/ColdTolerance.xml` is generated from them.
- The addon adds no C# or bundled DLL; it will use CCTO's existing XML extension.
- RimWorld 1.6 is the source-inspected target. No 1.7 VPE compatibility or native runtime PASS is claimed.

See [owner design](Docs/Design.md), [balance status](Docs/PlantBalance.json) and [active coordination](Docs/Coordination.md).

## Distribution and save considerations

- **Requirements:** RimWorld 1.6, Crop Cold Tolerance Overhaul and Vanilla Plants Expanded.
- **Save status:** The addon patches existing PlantDefs using XML only, without introducing save components or new plant definitions. Adding it to or removing it from an existing save has not been tested in-game. Living plants should adopt the updated temperature settings on loading; removing this addon cannot revive plants already killed by cold.
- **Public copy:** [combined Workshop EN/JA](Docs/SteamWorkshopDescription.txt) and [2game Japanese](Docs/2GameDescription-ja.txt); the current source-prepared version is 0.1.0. No other VPE plant-family addons are covered.
- **Packaging:** Run `python Scripts/build_release.py --output Dist/CCTO-for-VPE-0.1.0.zip`; this produces a strictly inventoried subscriber ZIP and performs payload validation, not game or Steam upload validation.
- **Existing public-item SteamCMD route:** [controlled publisher instructions](Docs/SteamCMDPrivatePublishing.md). Nonpublishing `preflight`/host checks are distinct from the separately approved manual `update_existing` operation for Workshop ID `3819497323`. The publisher must verify account ownership, exact item ID and retained public visibility; no new item, privacy switch or live update is implied by a source commit. Actual subscriber payload verification remains open.

## 日本語

CCTOとVanilla Plants Expanded向けの独立した任意互換Mod。

**実ゲーム未検証。** VPEの20種（通常14種と独自クラス6種）の耐寒性XMLを実装し、静的検証済み。作者はVPEを使用していないため、公開前の実機検証は必須とせず、利用者からの不具合報告をもとに修正する。症状・Mod構成・再現手順は [GitHub Issues](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/new/choose) に報告できる。数値はゲームバランス上の近似値。Steamには公開済みの既存アイテム `3819497323` があるが、現GitHub版の購読者配布ファイルとの一致は未確認。今後のアップロードは作者の別途承認が必要。既存セーブへの追加・削除は実ゲーム未検証。

VPE 1.6の独自植物クラス6種も追加対応した。植物固有の成長・開花・河川などの処理は置換しない。MOの対応は分離せず、CCTO本体に残す。

**VPE系列の追加植物Modへの耐寒性互換も本Modで一元管理する。** More Plants・Mushrooms・Succulents・Flowersは今後の対応候補で、現在は未実装。追加Modを必須依存にせず、各パックのPackage IDを確認した後に`LoadFolders.xml`の`IfModActive`で対象フォルダだけ読み込む。現在はVPE本体のXMLのみを読み込み、追加パック用XMLは未実装。

## Custom behavior / 独自実装の注意

Six plants retain VPE-specific code: Peas (rain bonus), Eggplant (temperature multipliers), Cabbage (toxic-fallout growth pause), Beet (winter growth logic), Cherry tree (winter blossom graphics), and Orange tree (river bonus). Their cold-tolerance XML is implemented, but interactions with that code are untested in-game and may cause bugs or unexpected growth, dormancy or display behavior. See the [source audit](Docs/Research/VpeCustomPlantClassAudit.md); report reproducible problems through GitHub Issues.

独自実装がある6種：エンドウ豆（雨の成長ボーナス）、ナス（温度別成長倍率）、キャベツ（有毒降下物中の成長停止）、ビート（冬季成長）、サクラ（冬季開花表示）、オレンジ（河川の成長ボーナス）。耐寒性XMLは実装済みだが、独自処理との組み合わせは実ゲーム未検証で、不具合や想定外の成長・休眠・表示が起きる可能性がある。再現できる問題はGitHub Issuesへ報告してほしい。
