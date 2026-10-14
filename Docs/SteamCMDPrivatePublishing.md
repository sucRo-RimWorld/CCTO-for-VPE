# CCTO for VPE — PRIVATE-ONLY SteamCMD Workshop publishing

## Current publisher decision — 2026-10-14 (supersedes historical YADA instructions)

**Future Workshop uploads must not use YADA.** The author's latest upload
using YADA is historical; the author reports the tags on the retained item
`3819497323` are already reflected. Do not repeat a Steamworks tag update
solely to reproduce that completed operation. For **future** CCTO for VPE
releases the approved tooling path is the repository's **manual**
`steam-private.yml` GitHub Actions pipeline: source/ZIP `preflight` →
separate WSL `steamcmd-private-publisher` `upload_private` for the
existing ID only → interactive Windows `steamworks-tag-publisher`
`sync_tags` for About-derived `Mod` and version tags. SteamCMD is responsible
for file upload; Steamworks handles tags. The non-mutating
`tag_runner_check` is still required as a first connectivity/identity
test of the newly registered Windows runner and **does not reapply tags**.

Do not treat the author's completed YADA upload or a successful Windows local
Steamworks probe as evidence that GitHub Actions has completed its
`tag_runner_check` or that future automated content updates work. Before
any subsequent `upload_private`, reconcile the **actual WSL publisher's**
`CCTO_STEAM_STATE` with Workshop ID `3819497323`, creator identity and
private visibility. A mismatched host state is a safety stop, not reason to
create a new item or overwrite the state. Maintain protected approval and no
public visibility transition. This section supersedes any older examples
that mention YADA as an ongoing uploader or initial new-item creation.


**Decision (2026-10-13):** Uploads orchestrated from ChatGPT/GitHub Actions must **create or update only an author-private** RimWorld Workshop item; public publication requires a separate explicit author decision and a different process. This is a scoped **CCTO for VPE** publisher, not a change to the Project shared native RimWorld test-host architecture and not evidence of Steam login/upload. Game testing remains author-waived for this optional addon.

## Implementation and safety gates

- `.github/workflows/steam-private.yml` is **manual `workflow_dispatch` only**, never push or pull-request triggered. Default **`preflight`** mode runs source tests, reviews a six-file subscriber ZIP and prepares a VDF with **private visibility `2`** without Steam access.
- Real **`upload_private`** mode requires an exact 40-character current `main` SHA (`exact_main_sha`) and the literal `PRIVATE_ONLY`. It runs only from this repository's `main`, with a GitHub protected environment `steam-workshop-private` and a dedicated **Linux self-hosted runner** labeled `steamcmd-private-publisher`. Public, friends-only, unlisted and arbitrary input visibility are deliberately not implemented. Do not run this on an untrusted PR runner or use the general game-test runner.
- The publisher script compares the candidate ZIP **byte-for-byte** with the immutable source checkout, accepts only six reviewed runtime/legal files, validates metadata/title/description and writes a SteamCMD VDF for RimWorld AppID `294100`, `visibility=2`, the approved Preview, English/Japanese description and the current changelog heading. It invokes `steamcmd +login USERNAME +workshop_build_item FILE +quit` only in explicit execute mode.
- Steam account password, Steam Guard code, cached credentials and authentication tickets are **never** GitHub secrets, repository files or script arguments. Authentication is provisioned **interactively on the isolated runner itself** under the restricted SteamCMD service account; the workflow may fail if Steam reauthentication becomes necessary. ChatGPT receives no credentials.
- Workshop ID is durable publisher-host state **outside the checkout**, in a 0600 file under a 0700 folder. `create_new_item` must be explicitly enabled for a first-time private item, with **no existing state**. Subsequent invocations update the saved ID and refuse a duplicate creation. SteamCMD writes the new ID to the VDF; it is saved even after an unsuccessful command when a real ID is detected to reduce accidental duplicate creation. If the item was created but SteamCMD did not return an ID, verify the Steam account's Workshop items before retrying.
- Every reported upload records `private_verified=false`. **A successful command alone does not prove the item is private or that Steam serves the expected content.** The owner must inspect the item as the authenticated creator, check visibility and the downloaded subscriber payload, then set `private_verified=true` in the host-local state before a subsequent update.
- A protected GitHub environment with explicit author/reviewer approval is recommended. Merely specifying `environment:` in YAML does not prove it has reviewer protection. Avoid account credentials on public/ephemeral runners. Keep host account and game installation isolated from ordinary gameplay and native-test profiles.

## Required one-time runner provisioning (not yet performed by this source change)

1. Provision a dedicated persistent Linux publisher environment trusted by the author. Install SteamCMD using the OS-supported mechanism; make the actual executable available and executable. Never copy a live player's Steam Guard data, personal saves or full game root to GitHub.
2. Register a **self-hosted GitHub Actions runner** with labels `self-hosted`, `linux`, and unique `steamcmd-private-publisher`, restricted to this owner repository and trusted user workflows. Do not assign this label to general self-hosted workers.
3. In the dedicated OS account/session, log into SteamCMD **interactively** to establish a valid cached Steam authentication and accept any Steam Guard/Workshop agreements. Steam account must be eligible to upload a RimWorld (AppID `294100`) Workshop item. Do not run `+login user password` in GitHub Actions.
4. Set these **local service environment variables**, outside repository or GitHub secrets: `CCTO_STEAMCMD_BIN` (absolute executable), `CCTO_STEAM_ACCOUNT` (Steam login name), `CCTO_STEAM_STATE` (persistent absolute JSON file under a private 0700 folder, *not* within GitHub checkout, e.g. an isolated `$HOME/.private/ccto-for-vpe-state.json`). Never set them via `workflow_dispatch` inputs.
5. In GitHub Settings → Environments, configure `steam-workshop-private` protection with an appropriate required reviewer where available. Restrict workflow runs to trusted repository administrators; ensure `contents:read` token and no pull-request entry. Test the label, SteamCMD executable and credentials locally before live dispatch.

## Operational troubleshooting and artifact digest contract

- On the dedicated WSL publisher, GitHub checkout/download can intermittently fail with `Could not resolve host: github.com` even after a transient successful `getent`. Check `getent ahostsv4 github.com` and `curl -4 -fIL --max-time 20 https://github.com` from the **publisher Linux account**; restore WSL DNS/network before retrying. GitHub-hosted preflight PASS does not prove the local publisher's DNS health. Do not bypass certificate verification, add pinned GitHub IP addresses, or store GitHub tokens as a DNS workaround.
- The preflight stores `Dist/sha256.txt` with a **filename relative to `Dist/`**. The publisher downloads the artifact into `Dist/`, changes into that directory, and runs `sha256sum -c sha256.txt` before SteamCMD. The publisher also independently compares ZIP bytes to the current approved main checkout. Never weaken either check to work around missing files.
- [Failed first upload attempt #38422572626](https://github.com/sucRo-RimWorld/CCTO-for-VPE/actions/runs/38422572626): preflight PASS, intermittent publisher DNS errors during checkout, then a deterministic `Dist/Dist/` checksum pathname failure. The SteamCMD upload step was **skipped**, so this run neither created nor updated a Steam item. Correct the checksum path and complete PR/main checks before a fresh, explicitly authorized `upload_private` dispatch. Keep the initial-create state gate; do not assume an item ID from a failed GitHub job.

## Publisher runner connectivity diagnostic (no Workshop upload)

After repeated WSL host-only DNS failures in `actions/checkout@v4` and `actions/download-artifact@v4`, use the manual **`runner_check`** mode **before any further `upload_private` attempt**. It runs the already-approved `preflight` on GitHub-hosted Linux, then dispatches a *nonpublishing* job on the same labeled `steamcmd-private-publisher` self-hosted runner and `steam-workshop-private` environment as the upload job. On that host, the job checks out the pinned current `main`, downloads the preflight artifact and verifies `Dist/sha256.txt` from inside `Dist/`.

To run: Actions → `CCTO for VPE SteamCMD private upload` → **Run workflow** (not **Re-run jobs**) → branch `main`; select `mode=runner_check`, exact current `main` 40-character SHA, `create_new_item=false`, **empty** `confirmation`. This mode has no SteamCMD step, cannot create or update a Workshop item and leaves the local PublishedFileId state untouched. It does not verify authenticated Steam access, current Workshop visibility or native-game behavior.

- If `runner_check` fails while GitHub Actions is **setting up the job**, inspect whether the action archive came from `codeload.github.com`; this occurs before any workflow shell step executes. An independent `curl` test in an interactive shell does not demonstrate the .NET runner downloader works under systemd.
- If it passes, the checkout / action-download / artifact-transfer / checksum path worked **in that one run**. It does **not** prove intermittent DNS is permanently fixed. Keep separate authorization and state checks for any actual private upload.
- Recent failing examples: [#38429405504](https://github.com/sucRo-RimWorld/CCTO-for-VPE/actions/runs/38429405504), [#38432806373](https://github.com/sucRo-RimWorld/CCTO-for-VPE/actions/runs/38432806373). Both had hosted `preflight` PASS and publisher setup FAIL resolving `codeload.github.com`; the SteamCMD step never ran. Host diagnosis is tracked in [issue #17](https://github.com/sucRo-RimWorld/CCTO-for-VPE/issues/17).

## Dispatch and verification

Use **Actions → CCTO for VPE SteamCMD private upload → Run workflow**, choose `main`, copy the exact current `main` SHA into `exact_main_sha`.

- **Offline rehearsal:** leave `mode=preflight`, `create_new_item=false`; empty confirmation. It runs hosted static/preview/ZIP checks and produces a 7-day audit artifact. Steam is not contacted, and a registered self-hosted runner is not required.
- **Initial private creation:** `mode=upload_private`, `create_new_item=true`, `confirmation=PRIVATE_ONLY`; requires the dedicated, authenticated runner. The host-state file must not exist. This operation creates a **new private-only** item if SteamCMD supports it for that account.
- **Later private update:** after confirming the Workshop item is private and the actual downloaded subscriber payload matches the six-file source package, set the host-local state JSON `private_verified` field to `true` using restricted local access. Re-dispatch with `mode=upload_private`, `create_new_item=false`, `confirmation=PRIVATE_ONLY`. Preserve the original `publishedfileid`; do not invent or overwrite it with an unrelated Steam ID.

For an already existing item, first inspect its ownership/visibility and initialize the private state file with a verified numeric `publishedfileid`, `appid=294100`, `schema_version=1`, `private_verified=true`, file mode 0600; never initialize it with `0` if the item already exists. The uploader will **only** set it to private; it must never be used to update a public item without explicit separate authorization and manual review.

SteamCMD command success is *not* native RimWorld behavior PASS, public visibility evidence or downloaded-payload verification. **No actual Steam private upload is claimed until a host workflow produces an ID and the owner confirms item visibility.** Never add an automatic public-publish step. If the author later chooses public release, that is a separate authorized task, with Steam privacy/metadata inspection and a new policy review.

References: [Steamworks Workshop implementation](https://partner.steamgames.com/doc/features/workshop/implementation) and [Steamworks visibility enum](https://partner.steamgames.com/doc/api/isteamremotestorage); `2` is Private, `0` is Public. Existing owner [ReleaseChecklist](ReleaseChecklist.md) remains authoritative for actual subscriber verification. The native-test host is a separate Project workstream and is **not** provisioned here.

## Description newline contract and first private item evidence

Workshop descriptions must retain real LF line breaks inside the quoted VDF value. Do not serialize description line breaks as the two characters `\n`: the first real SteamCMD upload displayed those characters literally. `vdf_quote` normalizes CRLF/CR to LF while preserving actual LF; quote/backslash escaping and private-only visibility remain enforced. The offline regression checks the complete approved bilingual description, not just a single-line fixture. Steam-side rendering still requires inspection after an update.

The author confirmed a successful private upload on 2026-10-14 and reported literal `\\n` in the description. Actual corrected Steam description and downloaded subscriber payload remain unverified. Preserve the existing item when correcting formatting; do not create a replacement item.


## Workshop version tags and complete changenotes (2026-10-14 source audit)

The original SteamCMD uploader reads `About/About.xml` for the title and
`About/Changelog.txt` for a `changenote`, but does **not** set Workshop
category/version tags. Unlike RimWorld's own upload path, SteamCMD does not
automatically turn `<supportedVersions>` into Workshop tags. Do not add a
nonfunctional `tags` field to the VDF and declare success. SteamCMD tag
submission is not a reliable supported path; use a properly authenticated
Steamworks `SetItemTags` call (with `Mod` plus all current
`About/About.xml` `supportedVersions`) or have the author set tags in
the Steam Workshop UI. The existing WSL SteamCMD session alone does not
establish a working desktop-Steam Steamworks session. A separate, safely
provisioned Steamworks metadata adapter is required for automation.

`Scripts/steamcmd_private.py` now validates the supported-version list,
reports the **expected** Workshop tags during offline preflight, and extracts
the *complete current-version changenote block* (not just the heading) from
`About/Changelog.txt`. This full note is supplied to SteamCMD's documented
`changenote` VDF field. Its presence in the generated VDF is source-only
evidence. SteamCMD success cannot prove that Steam created a change-note
history entry; creation of a first item may have different behavior from
updating an existing item. Verify the Steam Change Notes tab after a real
private update. Existing historical entries cannot be rewritten by changing
the file in GitHub; a later Steamworks `SubmitItemUpdate` may create a
*new* changenote entry instead.

The current private-upload action remains unchanged: metadata correction or
Steamworks integration must never bypass its author approval, ownership,
existing item ID, and private-only gates. No new Steamworks credentials or
desktop Steam installation are provisioned by this source change.


## Existing item identity lock — 2026-10-14

The author designated **Workshop 3819497323** as the item currently retained
for CCTO for VPE. A YADA upload created a *different* Workshop item; that
duplicate item's ID and creator-side history are not yet independently audited.
Do **not** delete any Workshop item merely by inference.

- The canonical repository `About/PublishedFileId.txt` now contains
  `3819497323` followed by LF; the local **installed** Mod folder used by
  YADA must contain the same file. Merely updating GitHub does not copy the
  file into the user's installed RimWorld Mods folder.
- `Scripts/build_release.py` validates and includes this file in the new
  seven-file release candidate. `Scripts/steamcmd_private.py` rejects host
  state with any different `publishedfileid`, even if private_verified;
  it also refuses `--create-new`. SteamCMD may update only this existing ID.
- The previously supported *initial creation* procedure above was applicable
  to the original pre-item phase only; it is **disabled** now that the
  author selected an existing item. `create_new_item` must remain false.
- The persistent host state (`CCTO_STEAM_STATE`) is **not readable from
  GitHub**. Do not silently overwrite it, set `private_verified=true`,
  or use a guessed ID. First reconcile the host's saved ID and actual item
  ownership/visibility; mismatches must fail closed.
- The Steam page could not be independently retrieved using unauthenticated
  public access in this task. The owner's designated item identity is a user
  instruction; live private visibility, remote changelog, Workshop tags and
  subscribed payload remain separately unverified.


## Authenticated Steamworks category-tag sync — integrated source, host pending

**2026-10-14:** The SteamCMD VDF cannot itself apply Workshop category tags.
The owner workflow now includes a separate `sync_tags` job using
`Scripts/steamworks_tags.py`, which delegates to
[pardeike/SteamWorkshopAgent](https://github.com/pardeike/SteamWorkshopAgent)
(`set-tags`, Steamworks API) on a dedicated **Windows interactive desktop
Steam session**. The integration uses the CLI contract inspected at upstream
source revision `c58f903d1e0220c395c8e305e1b9d3177db6df32`. No binary
is fetched from the internet in an authenticated runner job. Keep the
preinstalled agent version checked against this contract before using it.

Workflow behavior:

- `mode=sync_tags_private`, `create_new_item=false`,
  `confirmation=TAGS_PRIVATE_ONLY`: run the existing hosted source preflight,
  then the tag-only Windows runner. No SteamCMD content upload.
- `mode=upload_private`, `create_new_item=false`,
  `confirmation=PRIVATE_ONLY`: run the existing Linux SteamCMD publisher,
  then run `sync_tags` **only if the SteamCMD job succeeded**. Tag sync
  failure/pending runner is not success; do not treat publication as complete.
- `preflight` and `runner_check` do not contact Steamworks.
- The category tags come exclusively from the exact main checkout's
  `About/About.xml` (currently `Mod` and `1.6`), and the item ID comes
  from the pinned `About/PublishedFileId.txt` (`3819497323`).
- Tag updates never call `new-mod`, `publish`, SteamCMD, or visibility
  setters. The agent's `set-tags` command uses
  `ISteamUGC::SetItemTags` + `SubmitItemUpdate`, with a short, bilingual
  tag-maintenance note. Existing Workshop content and visibility are not
  requested to change.
- A Steam session probe must return authenticated Steamworks for app 294100
  before submission. An on-host private receipt records a `PENDING` intent
  *before* the Steamworks call. A timeout/failed/ambiguous result blocks
  automatic retry; only a proven `OK` result writes the completed receipt.
  A repeated tag-only request with an `OK` receipt is skipped. **Every successful
  content upload** uses its unique GitHub workflow run ID to refresh tags once,
  even if an earlier tag-only request succeeded; reruns for the same workflow
  run ID are skipped. An ambiguous `PENDING` receipt always blocks retry.
  A local receipt is **not** remote tag read-back.

**Required host provisioning; not yet verified:**

1. Run a second, dedicated self-hosted GitHub runner on **Windows in the same
   interactive user session as the logged-in, online Steam desktop client**.
   Label it `steamworks-tag-publisher` with standard `self-hosted` and
   `windows` labels. Do not run the tag runner as a Session 0 Windows
   service; `SteamAPI_Init` may not see the desktop Steam account there.
   This is separate from WSL's `steamcmd-private-publisher` service.
2. Install a reviewed Windows x64 build of SteamWorkshopAgent and .NET 10
   runtime on the trusted machine; provision `STEAMWORKS_NATIVE_LIB` to
   RimWorld's correct `steam_api64.dll` path. Upstream currently defaults to
   macOS library discovery, so the Windows override is essential.
   Test the upstream `steam-session-probe` in the exact interactive runner
   context, not from a different user's shell.
3. Provision **host-local** `CCTO_STEAMWORKS_AGENT_BIN` (absolute executable)
   and `CCTO_STEAM_TAG_RECEIPT` (under that user's `LOCALAPPDATA`, with
   user-private NTFS permissions). Do not store tokens, Steam login passwords,
   private receipt files or Steam authenticator data in GitHub. The checkout
   is never used to install/overwrite the agent.
4. Reconcile creator ownership and the item being private *on Steam* before
   granting the protected `steam-workshop-private` environment approval.
   A SteamCMD login may invalidate the concurrent desktop session; the probe
   will fail closed rather than guessing. Keep tag and content runners
   isolated even when installed on the same physical PC.
5. After an accepted tag update, inspect the actual retained Workshop item
   `3819497323` as its creator, verify the `Mod`/version tags and current
   private visibility, and record this as Steam-side evidence. The agent's
   callback and the local receipt alone prove neither Steam page read-back
   nor subscriber contents. A failed/ambiguous `PENDING` receipt requires
   an explicit human/owner reconciliation before any retry. Don't delete it
   or dispatch another update blindly.

The owner Python tests mock SteamWorkshopAgent; they demonstrate guards and
workflow structure only. This source integration does not mean that the
second runner, Windows native DLL, authenticated desktop session, or actual
Steam tag setting is installed/working. No live Workshop mutation has
been performed by this change.

## Windows host bootstrap and nonpublishing acceptance (2026-10-14)

The existing Windows Steam session cannot be accessed from GitHub source-control
tools. The *working host* and *actual Steam tag visibility* remain unverified.
Do not label the tag infrastructure LIVE merely because the repository CI passed.

Use the owner-managed `Scripts/Prepare-WindowsSteamworksTagRunner.ps1` from a
**PowerShell 7 interactive session**, not elevated and not a Windows service.
It keeps the Steamworks binary/receipt below the logged-in Windows user's
`LOCALAPPDATA`. It checks for desktop Steam **in the same Windows session**,
detects exactly one native `steam_api64.dll` within the installed RimWorld
root, builds a reviewed/pinned upstream agent from commit
`c58f903d1e0220c395c8e305e1b9d3177db6df32` only when requested,
and runs the agent's **read-only `steam-session-probe`**. It prints SHA-256
hashes of the agent executable and native library but not Steam credentials.
An upstream .NET 10 SDK and Git are required only for `-BuildPinnedAgent`;
Python must also be in the interactive runner's PATH.

Example from the reviewed CCTO-for-VPE checkout on the user's **own**
Windows machine (change the RimWorld installation path if applicable):

```powershell
pwsh -NoProfile -File .\Scripts\Prepare-WindowsSteamworksTagRunner.ps1 -RimWorldRoot 'D:\SteamLibrary\steamapps\common\RimWorld' -BuildPinnedAgent
```

This command only builds/probes; it does not register a GitHub runner and
does not change tags. A successful direct PowerShell probe still does not
prove the Actions runner runs in that same Windows login session.

Register a **separately authorized** self-hosted Windows runner to the
`sucRo-RimWorld/CCTO-for-VPE` repository, with the labels
`self-hosted`, `windows`, and `steamworks-tag-publisher`. Use the
repository's GitHub Settings > Actions > Runners > New self-hosted runner
flow. Registration token is short-lived and entered **locally only**.
Do not run `svc install`, `svc start` or Windows Service Manager for
this interactive desktop-Steam runner. The dedicated WSL SteamCMD runner
has a different label and separate host-level Steam credentials.

After runner registration, launch the registered runner from the same logged
Steam Windows account. This process-scoped launcher performs the same
nonpublishing Steamworks probe first; the actual runner inherits the two
`CCTO_...` variables and `STEAMWORKS_NATIVE_LIB` only through its process
environment, not through GitHub secrets.

```powershell
pwsh -NoProfile -File .\Scripts\Prepare-WindowsSteamworksTagRunner.ps1 -RimWorldRoot 'D:\SteamLibrary\steamapps\common\RimWorld' -RunnerHome 'C:\actions-runner-steamworks' -RunRegisteredRunner
```

The runner directory is an example, not evidence it has been installed.
Never reuse a general PR/native-game runner, save root or Steam credentials.

With the Windows runner online, GitHub Actions
`CCTO for VPE SteamCMD private upload` now has
`mode=tag_runner_check` (exact **current** main SHA,
`create_new_item=false`, empty confirmation). It runs the hosted source
tests followed by the **Windows session probe only**. It has no
`set-tags`, `--sync`, or SteamCMD upload step. Only after this check
passes and the existing item has been independently verified private
should a separate manual `sync_tags_private`/ `TAGS_PRIVATE_ONLY`
dispatch be considered. No Steam job is dispatched by documentation edits.

If the probe fails, investigate the exact native library, binary architecture,
Steam logged-on state and runner session isolation. Do **not** change service
privileges, copy authentication files between users, disable repository guards
or blindly retry a `PENDING` tag operation.

**Windows compatibility remains conditional:** SteamWorkshopAgent's upstream
documentation and automatic library discovery target macOS; supplying a Windows
`steam_api64.dll` is supported by its environment override, but actual
native ABI, SteamAPI_Init and SetItemTags on this author's PC have not been
tested. Source-level CI cannot verify the native behavior.
