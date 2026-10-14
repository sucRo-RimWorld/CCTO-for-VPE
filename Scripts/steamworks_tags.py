#!/usr/bin/env python3
"""Sync tags only, via authenticated SteamWorkshopAgent (no content upload).

Only use on the dedicated, logged-in desktop Steamworks runner. Does not
create Workshop items, update their visibility, or use SteamCMD credentials.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from build_release import EXPECTED_WORKSHOP_ID
from steamcmd_private import APPID, workshop_tags

ROOT = Path(__file__).resolve().parents[1]
NOTE = 'Update RimWorld compatibility tags / 対応バージョンのタグ更新'
CONFIRM = 'TAGS_PRIVATE_ONLY'


def expected_metadata(checkout: Path) -> tuple[str, ...]:
    id_path = checkout / 'About/PublishedFileId.txt'
    if id_path.read_text(encoding='ascii').strip() != EXPECTED_WORKSHOP_ID:
        raise ValueError('Workshop ID differs from the author-selected existing item')
    about = ET.fromstring((checkout / 'About/About.xml').read_bytes())
    if about.findtext('packageId') != 'sucro.cctoforvpe':
        raise ValueError('Unexpected Mod packageId')
    return workshop_tags(about)


def receipt_path_ok(path: Path, checkout: Path) -> Path:
    if path.is_symlink():
        raise ValueError('Receipt must not be a symlink')
    path = path.expanduser().resolve()
    if checkout.resolve() == path or checkout.resolve() in path.parents:
        raise ValueError('Receipt must be outside the GitHub checkout')
    if os.name == 'nt':
        # Windows does not implement POSIX 0600 semantics. Confine host-only
        # receipts to the signed-in user's profile and its NTFS ACLs.
        root = os.environ.get('LOCALAPPDATA')
        if not root or not path.is_relative_to(Path(root).resolve()):
            raise ValueError('Windows receipt must be under the Steam runner LOCALAPPDATA')
        if path.exists() and not path.is_file():
            raise ValueError('Receipt must be a regular file')
    else:
        if path.exists() and (not path.is_file() or stat.S_IMODE(path.stat().st_mode) & 0o077):
            raise ValueError('Receipt must be a private 0600 file')
        if path.parent.exists() and stat.S_IMODE(path.parent.stat().st_mode) & 0o077:
            raise ValueError('Receipt parent must be a private 0700 directory')
    return path


def run_agent(agent: Path, args: list[str], timeout: int = 210) -> dict:
    proc = subprocess.run([str(agent), *args], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=timeout, check=False)
    # Never print external tool stderr, which might include desktop/user details.
    if proc.returncode != 0:
        raise RuntimeError('SteamWorkshopAgent command failed: ' + args[0])
    try:
        envelope = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as exc:
        raise RuntimeError('SteamWorkshopAgent returned invalid JSON') from exc
    if not isinstance(envelope, dict) or envelope.get('status') != 'ok':
        raise RuntimeError('SteamWorkshopAgent returned a non-success envelope')
    data = envelope.get('data')
    if not isinstance(data, dict):
        raise RuntimeError('SteamWorkshopAgent returned no result object')
    return data


def _receipt_matches(path: Path, tags: tuple[str, ...], context: str = 'tag-only') -> bool:
    if not path.exists():
        return False
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeError):
        raise ValueError('Invalid publisher receipt; stop instead of retrying an ambiguous update')
    if (obj.get('schema') != 1 or obj.get('publishedfileid') != EXPECTED_WORKSHOP_ID
            or obj.get('appid') != APPID):
        raise ValueError('Receipt identity mismatch; do not overwrite existing state')
    if obj.get('steamworks_submit_result') == 'PENDING':
        raise ValueError('Prior tag submission may have started; verify Steam before any retry')
    if obj.get('steamworks_submit_result') != 'OK':
        raise ValueError('Invalid Steamworks receipt status')
    return obj.get('tags') == list(tags) and obj.get('context') == context


def _store_receipt(path: Path, tags: tuple[str, ...], result: str = 'OK', context: str = 'tag-only') -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != 'nt' and stat.S_IMODE(path.parent.stat().st_mode) & 0o077:
        raise ValueError('Receipt parent must be private')
    obj = {
        'schema': 1, 'publishedfileid': EXPECTED_WORKSHOP_ID,
        'appid': APPID, 'tags': list(tags), 'context': context,
        'steamworks_submit_result': result,
        'steam_page_readback_verified': False,
    }
    fd, tmp = tempfile.mkstemp(prefix='.steam-tags-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(obj, out, ensure_ascii=False, sort_keys=True)
            out.write('\n')
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def check_session(agent: Path) -> None:
    probe = run_agent(agent, ['steam-session-probe'], timeout=90)
    if (probe.get('ready') is not True or probe.get('steamUserLoggedOn') is not True
            or probe.get('steamAppId') != int(APPID)):
        raise RuntimeError('Steam desktop session for RimWorld is not authenticated')


def sync(checkout: Path, agent: Path, receipt: Path, confirmation: str,
         after_upload_run_id: str | None = None) -> str:
    tags = expected_metadata(checkout)
    if confirmation != CONFIRM:
        raise ValueError('Explicit TAGS_PRIVATE_ONLY confirmation required')
    if not agent.is_file() or not os.access(agent, os.X_OK):
        raise ValueError('SteamWorkshopAgent executable is not provisioned')
    if checkout.resolve() == agent.resolve() or checkout.resolve() in agent.resolve().parents:
        raise ValueError('SteamWorkshopAgent binary must be outside checkout')
    receipt = receipt_path_ok(receipt, checkout)
    if after_upload_run_id is not None and not re.fullmatch(r'[1-9][0-9]{0,19}', after_upload_run_id):
        raise ValueError('Invalid post-upload GitHub workflow run ID')
    # A successful SteamCMD content update must refresh tags once per *upload*.
    # A prior OK tag-only receipt cannot establish tags survived that upload.
    context = 'after-upload:' + after_upload_run_id if after_upload_run_id else 'tag-only'
    if _receipt_matches(receipt, tags, context):
        return 'SKIPPED: same tags and operation have a local OK receipt; Steam page not reverified'

    check_session(agent)
    # Intent is durable before the potentially ambiguous Steam submission.
    # An aborted/crashed run remains PENDING and cannot silently retry.
    _store_receipt(receipt, tags, result='PENDING', context=context)
    # Numeric target + explicit tags avoids parsing an untrusted local mod path.
    # The agent calls only StartItemUpdate/SetItemTags/SubmitItemUpdate.
    result = run_agent(agent, ['set-tags', EXPECTED_WORKSHOP_ID, *tags, '--confirm',
                               '--changenote', NOTE])
    if (result.get('success') is not True
            or str(result.get('publishedFileId')) != EXPECTED_WORKSHOP_ID
            or result.get('steamAppId') != int(APPID)
            or result.get('steamUserLoggedOn') is not True
            or result.get('submitResult') != 'OK'
            or result.get('timedOut') is not False
            or result.get('userNeedsToAcceptWorkshopLegalAgreement') is not False
            or result.get('tags') != list(tags)):
        # Do not retry on an ambiguous result: Steam may have accepted it.
        raise RuntimeError('Steamworks tag submit result unverified; inspect Steam before retrying')
    _store_receipt(receipt, tags, context=context)
    return 'SUBMITTED: tag update acknowledged by Steamworks; remote Workshop page not verified'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkout', type=Path, default=ROOT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--sync', action='store_true', help='Submit tags via Steamworks')
    group.add_argument('--probe', action='store_true', help='Check authenticated Steamworks only; never mutate tags')
    parser.add_argument('--after-upload-run-id', default=None,
                        help='One-shot refresh context for the exact successful GitHub content-upload run')
    parser.add_argument('--confirm', default='')
    args = parser.parse_args()
    tags = expected_metadata(args.checkout)
    if not args.sync and not args.probe:
        if args.after_upload_run_id:
            raise ValueError('An upload run ID requires --sync')
        print('OFFLINE tags:', ', '.join(tags), '; Workshop ID:', EXPECTED_WORKSHOP_ID,
              '; no Steam contact')
        return 0
    if args.probe and args.after_upload_run_id:
        raise ValueError('A probe cannot be tied to an upload mutation')
    agent = os.environ.get('CCTO_STEAMWORKS_AGENT_BIN')
    receipt = os.environ.get('CCTO_STEAM_TAG_RECEIPT')
    if not agent or not receipt:
        raise ValueError('Trusted desktop runner must configure CCTO_STEAMWORKS_AGENT_BIN and CCTO_STEAM_TAG_RECEIPT locally')
    if args.probe:
        receipt_path_ok(Path(receipt), args.checkout)
        if not Path(agent).is_file() or not os.access(agent, os.X_OK):
            raise ValueError('SteamWorkshopAgent executable is not provisioned')
        check_session(Path(agent))
        print('READY: Steamworks authenticated for RimWorld; no Workshop mutation')
    else:
        print(sync(args.checkout, Path(agent), Path(receipt), args.confirm,
                   after_upload_run_id=args.after_upload_run_id))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired, ET.ParseError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
