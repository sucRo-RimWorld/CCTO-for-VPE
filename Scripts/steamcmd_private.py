#!/usr/bin/env python3
"""Strict PRIVATE-only SteamCMD UGC staging/upload; author-runner credentials stay on host."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

from build_release import FILES, FOLDER, check_zip

ROOT = Path(__file__).resolve().parents[1]
APPID = '294100'
VISIBILITY = '2'  # Steamworks enum: Private, visible only to creator
STATE_SCHEMA = 1
TITLE_LIMIT = 128
DESC_BYTE_LIMIT = 8000


def vdf_quote(value: str) -> str:
    if any(ord(char) < 32 and char not in '\r\n\t' for char in value):
        raise ValueError('Control characters are not valid in a Workshop VDF')
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '\\n').replace('\t', '\\t') + '"'


def validate_zip_and_copy(zip_path: Path, checkout: Path, stage: Path) -> tuple[Path, Path, str, str, str]:
    """Compare all ZIP bytes against the exact checked-out release sources."""
    check_zip(zip_path)
    content = stage / 'CCTO-for-VPE'
    content.mkdir(mode=0o700)
    with zipfile.ZipFile(zip_path) as bundle:
        for rel in FILES:
            blob = bundle.read(FOLDER + rel)
            if blob != (checkout / rel).read_bytes():
                raise ValueError('Release ZIP is not byte-for-byte equal to checked-out source: ' + rel)
            target = content / rel
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(blob)
    preview = content / 'About/Preview.png'
    metadata = ET.fromstring((content / 'About/About.xml').read_bytes())
    if metadata.findtext('packageId') != 'sucro.cctoforvpe':
        raise ValueError('Wrong Mod packageId')
    if metadata.findtext('modVersion') != '0.1.0':
        raise ValueError('Unexpected release version; audit the script before using a new version')
    title = metadata.findtext('name') or ''
    if not title or len(title) > TITLE_LIMIT:
        raise ValueError('Invalid Workshop title')
    description = (checkout / 'Docs/SteamWorkshopDescription.txt').read_text(encoding='utf-8')
    if '[hr][/hr]' not in description or '実ゲーム未検証' not in description:
        raise ValueError('Missing bilingual description or untested-game disclosure')
    if not (1 <= len(description.encode('utf-8')) <= DESC_BYTE_LIMIT):
        raise ValueError('Workshop description exceeds Steam length constraint')
    changelog = (content / 'About/Changelog.txt').read_text(encoding='utf-8')
    note = next((s.strip() for s in changelog.splitlines() if s.startswith('0.1.0 - ')), '')
    if not note:
        raise ValueError('No current version changelog')
    return content, preview, title, description, note


def make_vdf(content: Path, preview: Path, title: str, description: str,
             changenote: str, published_id: str) -> str:
    """No caller can choose public/friends/unlisted visibility or app ID."""
    if not re.fullmatch(r'0|[1-9][0-9]{0,19}', published_id):
        raise ValueError('Invalid PublishedFileId')
    fields = {
        'appid': APPID,
        'publishedfileid': published_id,
        'contentfolder': str(content.resolve()),
        'previewfile': str(preview.resolve()),
        'visibility': VISIBILITY,
        'title': title,
        'description': description,
        'changenote': changenote,
    }
    return '"workshopitem"\n{\n' + ''.join(f'  {vdf_quote(k)} {vdf_quote(v)}\n' for k, v in fields.items()) + '}\n'


def read_updated_id(text: str) -> str:
    match = re.search(r'^\s*"publishedfileid"\s+"([0-9]+)"\s*$', text, re.MULTILINE)
    if not match or not match.group(1).isdigit() or int(match.group(1)) <= 0:
        raise ValueError('SteamCMD did not write back a nonzero PublishedFileId')
    return match.group(1)


def check_state_path(state: Path, checkout: Path) -> None:
    if state.is_symlink():
        raise ValueError('Steam state must not be a symlink')
    state = state.expanduser().resolve()
    if not state.is_absolute() or state == checkout.resolve() or checkout.resolve() in state.parents:
        raise ValueError('Steam state must be kept outside the GitHub checkout')
    if state.parent.exists() and stat.S_IMODE(state.parent.stat().st_mode) & 0o077:
        raise ValueError('Steam state directory must be private (0700)')
    if state.exists():
        if not state.is_file() or stat.S_IMODE(state.stat().st_mode) & 0o077:
            raise ValueError('Steam state must be a private 0600 regular file')


def load_published_id(state: Path, create_new: bool) -> str:
    if not state.exists():
        if not create_new:
            raise ValueError('No saved Workshop ID. First creation must be explicitly authorized with --create-new')
        return '0'
    if create_new:
        raise ValueError('An item ID is already saved; refusing to create a duplicate')
    obj = json.loads(state.read_text(encoding='utf-8'))
    if obj.get('schema_version') != STATE_SCHEMA or obj.get('appid') != APPID:
        raise ValueError('Unexpected Steam state schema or appid')
    existing_id = obj.get('publishedfileid')
    if not isinstance(existing_id, str) or not re.fullmatch(r'[1-9][0-9]*', existing_id):
        raise ValueError('Invalid saved Workshop ID')
    if obj.get('private_verified') is not True:
        raise ValueError('Operator must confirm the existing Steam item is PRIVATE before updating')
    return existing_id


def store_state(path: Path, published_id: str, source_hash: str) -> None:
    """Private atomic state; uploaded != verified-private (requires Steam-side check)."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    document = {
        'schema_version': STATE_SCHEMA,
        'appid': APPID,
        'publishedfileid': published_id,
        'private_verified': False,
        'last_source_sha256': source_hash,
        'status': 'uploaded_visibility_unverified',
    }
    fd, filename = tempfile.mkstemp(prefix='.ccto-private-state-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write('\n')
        os.chmod(filename, 0o600)
        os.replace(filename, path)
    finally:
        if os.path.exists(filename):
            os.unlink(filename)


def run_upload(zip_path: Path, checkout: Path, state: Path, executable: Path,
               account: str, create_new: bool, confirmation: str) -> str:
    if confirmation != 'PRIVATE_ONLY':
        raise ValueError('Missing exact manual private-upload approval phrase')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', account):
        raise ValueError('Steam login name must be provisioned locally on the publisher host')
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError('SteamCMD executable missing or not executable')
    check_state_path(state, checkout)
    prev = load_published_id(state, create_new)
    original_zip_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    # Temporary staging is never under the repo and is deleted after the invocation.
    with tempfile.TemporaryDirectory(prefix='ccto-vpe-steam-private-') as temp:
        stage = Path(temp)
        content, preview, title, description, note = validate_zip_and_copy(zip_path, checkout, stage)
        vdf = stage / 'upload_private.vdf'
        vdf.write_text(make_vdf(content, preview, title, description, note, prev), encoding='utf-8')
        os.chmod(vdf, 0o600)
        local_log = stage / 'steamcmd.log'
        # Never pass password, Guard code or GitHub secret in argv, env interpolation or logs.
        with local_log.open('wb') as logfile:
            try:
                proc = subprocess.run([str(executable.resolve()), '+login', account,
                                       '+workshop_build_item', str(vdf), '+quit'],
                                      cwd=stage, stdin=subprocess.DEVNULL,
                                      stdout=logfile, stderr=subprocess.STDOUT,
                                      timeout=900, check=False)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError('SteamCMD timed out; authentication may need local reapproval') from exc
        # Valve updates the VDF with new PublishedFileId, even for newly created items.
        after = None
        try:
            after = read_updated_id(vdf.read_text(encoding='utf-8'))
        except ValueError:
            pass
        if after and (prev == '0' or after == prev):
            # Preserve an ID even after nonzero exit to avoid duplicate creation.
            store_state(state, after, original_zip_hash)
        if proc.returncode != 0:
            raise RuntimeError('SteamCMD returned nonzero status; inspect the runner-local private log. '
                               'If a new ID was allocated it has been preserved, but requires review.')
        if after is None:
            raise RuntimeError('SteamCMD reported success without a valid PublishedFileId; '
                               'stop and manually check the Workshop before retrying')
        if prev != '0' and after != prev:
            raise RuntimeError('SteamCMD changed an existing Workshop item ID unexpectedly')
        print('SteamCMD accepted private-only upload request for Workshop ID ' + after)
        print('Steam-side visibility and downloaded subscriber contents: NOT VERIFIED; author review required')
        return after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True, type=Path)
    parser.add_argument('--checkout', type=Path, default=ROOT)
    parser.add_argument('--execute', action='store_true', help='Actually contact Steam; no implicit upload')
    parser.add_argument('--confirm', default='', help='Must equal PRIVATE_ONLY for actual uploads')
    parser.add_argument('--create-new', action='store_true', help='Explicit first-time creation, not update')
    args = parser.parse_args()
    if not args.execute:
        with tempfile.TemporaryDirectory() as tmp:
            content, preview, title, description, note = validate_zip_and_copy(
                args.zip, args.checkout, Path(tmp))
            raw = make_vdf(content, preview, title, description, note, '0')
            if '"visibility" "2"' not in raw:
                raise ValueError('Private visibility guard did not survive VDF generation')
            print('Offline PRIVATE SteamCMD VDF and exact source ZIP validation PASS; NO UPLOAD')
        return 0
    steamcmd = os.environ.get('CCTO_STEAMCMD_BIN', '')
    account = os.environ.get('CCTO_STEAM_ACCOUNT', '')
    saved = os.environ.get('CCTO_STEAM_STATE', '')
    if not (steamcmd and account and saved):
        parser.error('Trusted runner must set CCTO_STEAMCMD_BIN, CCTO_STEAM_ACCOUNT, CCTO_STEAM_STATE locally')
    result = run_upload(args.zip, args.checkout, Path(saved), Path(steamcmd), account,
                        args.create_new, args.confirm)
    print('Unverified Workshop item URL: https://steamcommunity.com/sharedfiles/filedetails/?id=' + result)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, zipfile.BadZipFile) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
