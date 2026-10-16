#!/usr/bin/env python3
"""Existing Workshop item updater; preserve public visibility and host-only Steam credentials."""
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
from urllib import parse as urlparse, request as urlrequest

from build_release import FILES, FOLDER, EXPECTED_WORKSHOP_ID, check_zip

ROOT = Path(__file__).resolve().parents[1]
APPID = '294100'
EXPECTED_VISIBILITY = 0  # Existing item is PUBLIC; never set VDF visibility.
STATE_SCHEMA = 1
TITLE_LIMIT = 128
DESC_BYTE_LIMIT = 8000


def vdf_quote(value: str) -> str:
    if any(ord(char) < 32 and char not in '\r\n\t' for char in value):
        raise ValueError('Control characters are not valid in a Workshop VDF')
    # SteamCMD preserves escaped newline text literally in Workshop descriptions.
    # Keep real line breaks inside the quoted KeyValues value instead.
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\r\n', '\n').replace('\r', '\n').replace('\t', '\\t') + '"'


def current_changenote(changelog: str, version: str) -> str:
    """Get exactly the current version's complete change-note block, not just its title."""
    heading = re.compile(r'^(\d+(?:\.\d+){1,3})\s+-\s+\S')
    lines = changelog.splitlines()
    matches = [(i, match.group(1)) for i, line in enumerate(lines)
               if (match := heading.match(line))]
    positions = [index for index, found_version in matches if found_version == version]
    if len(positions) != 1:
        raise ValueError('Expected exactly one current-version changelog heading')
    start = positions[0]
    stop = next((index for index, _ in matches if index > start), len(lines))
    selected = [line for line in lines[start:stop] if not line.startswith('#')]
    result = '\n'.join(selected).strip()
    if not result or len(result.splitlines()) < 2 or not result.splitlines()[1].strip():
        raise ValueError('Current-version changelog has no body')
    return result


def workshop_tags(metadata: ET.Element) -> tuple[str, ...]:
    """Expected Steamworks tags; SteamCMD VDF does not reliably submit them."""
    versions = [(node.text or '').strip() for node in metadata.findall('./supportedVersions/li')]
    if not versions or len(set(versions)) != len(versions):
        raise ValueError('Missing or duplicated supported RimWorld versions')
    if any(not re.fullmatch(r'1\.\d+', version) for version in versions):
        raise ValueError('Invalid supported RimWorld version for Workshop tags')
    return ('Mod', *versions)


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
    published_id = (content / 'About/PublishedFileId.txt').read_text(encoding='utf-8').strip()
    if published_id != EXPECTED_WORKSHOP_ID:
        raise ValueError('Staged PublishedFileId differs from the authorized existing item')
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
    version = metadata.findtext('modVersion') or ''
    if not version:
        raise ValueError('Missing current Mod version')
    workshop_tags(metadata)
    note = current_changenote(changelog, version)
    return content, preview, title, description, note


def make_vdf(content: Path, preview: Path, title: str, description: str,
             changenote: str, published_id: str) -> str:
    """No caller can choose public/friends/unlisted visibility or app ID."""
    if published_id != EXPECTED_WORKSHOP_ID:
        raise ValueError('Existing-item VDF requires the exact retained PublishedFileId')
    fields = {
        'appid': APPID,
        'publishedfileid': published_id,
        'contentfolder': str(content.resolve()),
        'previewfile': str(preview.resolve()),
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


def verify_live_public_item() -> str:
    """Read Steam's live item details and fail closed on unknown visibility.

    This call does not authenticate to Steam or mutate a Workshop item.
    """
    endpoint = 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/'
    body = urlparse.urlencode({
        'itemcount': '1', 'publishedfileids[0]': EXPECTED_WORKSHOP_ID,
    }).encode('ascii')
    request = urlrequest.Request(endpoint, data=body, method='POST')
    try:
        with urlrequest.urlopen(request, timeout=20) as response:
            payload = json.load(response)
        items = payload['response']['publishedfiledetails']
        if not isinstance(items, list) or len(items) != 1:
            raise ValueError('Expected exactly one Workshop item detail')
        item = items[0]
        if (str(item.get('result')) != '1'
                or str(item.get('publishedfileid')) != EXPECTED_WORKSHOP_ID
                or item.get('title') != 'CCTO for VPE'
                or str(item.get('consumer_app_id', APPID)) != APPID):
            raise ValueError('Unexpected Steam Workshop item identity')
        if type(item.get('visibility')) is not int or item['visibility'] != EXPECTED_VISIBILITY:
            raise ValueError('Existing item is not PUBLIC (0); update blocked')
        creator = str(item.get('creator', ''))
        if not re.fullmatch(r'[1-9][0-9]{0,19}', creator):
            raise ValueError('Steam Workshop item creator unavailable')
        return creator
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError('Steam Workshop public identity/visibility verification failed: '
                         + str(exc)) from exc


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
    if create_new:
        raise ValueError('Creation disabled: CCTO updates an existing item only')
    if not state.exists():
        raise ValueError('No saved Workshop ID; do not create or replace the state automatically')
    obj = json.loads(state.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise ValueError('Unexpected Steam state document type')
    if obj.get('schema_version') != STATE_SCHEMA or obj.get('appid') != APPID:
        raise ValueError('Unexpected Steam state schema or appid')
    existing_id = obj.get('publishedfileid')
    if not isinstance(existing_id, str) or not re.fullmatch(r'[1-9][0-9]*', existing_id):
        raise ValueError('Invalid saved Workshop ID')
    return existing_id


def check_existing_host_state(state: Path, checkout: Path) -> None:
    """Read-only, fail-closed host gate; never edits state or contacts Steam."""
    check_state_path(state, checkout)
    saved_id = load_published_id(state, create_new=False)
    if saved_id != EXPECTED_WORKSHOP_ID:
        raise ValueError('Publisher host Workshop ID differs from retained item; no upload permitted')
    print('HOST STATE CHECK PASS: saved AppID, retained Workshop ID and file permissions')
    print('Workshop item ' + EXPECTED_WORKSHOP_ID
          + ': Steam-side owner/visibility/content NOT VERIFIED')


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
    if confirmation != 'UPDATE_EXISTING_ONLY':
        raise ValueError('Missing exact manual existing-item update confirmation')
    if not re.fullmatch(r'[A-Za-z0-9_]{1,64}', account):
        raise ValueError('Steam login name must be provisioned locally on the publisher host')
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError('SteamCMD executable missing or not executable')
    check_state_path(state, checkout)
    if create_new:
        raise ValueError('Creation disabled: About/PublishedFileId.txt defines the existing Workshop item')
    prev = load_published_id(state, create_new=False)
    if prev != EXPECTED_WORKSHOP_ID:
        raise ValueError('Publisher host Workshop ID differs from the author-selected existing item; refusing upload')
    # The public item must still be the expected item before SteamCMD runs.
    initial_creator = verify_live_public_item()
    original_zip_hash = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    # Temporary staging is never under the repo and is deleted after the invocation.
    with tempfile.TemporaryDirectory(prefix='ccto-vpe-steam-private-') as temp:
        stage = Path(temp)
        content, preview, title, description, note = validate_zip_and_copy(zip_path, checkout, stage)
        vdf = stage / 'upload_private.vdf'
        rendered = make_vdf(content, preview, title, description, note, prev)
        if '"visibility"' in rendered:
            raise ValueError('Visibility must be omitted from existing-item updates')
        vdf.write_text(rendered, encoding='utf-8')
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
        if after != prev:
            raise RuntimeError('SteamCMD changed an existing Workshop item ID unexpectedly')
        # A success return is insufficient: independently check the public item.
        if verify_live_public_item() != initial_creator:
            raise RuntimeError('Workshop creator changed; inspect Steam before any retry')
        print('SteamCMD accepted existing-item update for Workshop ID ' + after)
        print('SteamCMD changenote submitted (full current-version block); Steam history NOT VERIFIED')
        print('Workshop tags NOT UPDATED by SteamCMD: Steamworks metadata sync is required ('
              + ', '.join(workshop_tags(ET.fromstring((content / 'About/About.xml').read_bytes()))) + ')')
        print('Steam API confirmed public visibility unchanged; authenticated owner and downloaded content NOT VERIFIED')
        return after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path)
    parser.add_argument('--check-host-state', action='store_true',
                        help='Read-only publisher state check; no ZIP, login or upload')
    parser.add_argument('--checkout', type=Path, default=ROOT)
    parser.add_argument('--execute', action='store_true', help='Explicit existing-item update; contacts Steam')
    parser.add_argument('--confirm', default='', help='Must equal PRIVATE_ONLY for actual uploads')
    parser.add_argument('--create-new', action='store_true', help='Explicit first-time creation, not update')
    args = parser.parse_args()
    if args.check_host_state:
        if args.execute or args.create_new or args.confirm or args.zip is not None:
            parser.error('--check-host-state is read-only and accepts no upload options')
        saved = os.environ.get('CCTO_STEAM_STATE', '')
        if not saved:
            parser.error('CCTO_STEAM_STATE is not configured in the trusted publisher runner')
        check_existing_host_state(Path(saved), args.checkout)
        return 0
    if args.zip is None:
        parser.error('--zip is required for ZIP preflight or real uploads')
    if args.create_new:
        raise ValueError('Creation disabled: existing Workshop item ID is fixed in About/PublishedFileId.txt')
    if not args.execute:
        with tempfile.TemporaryDirectory() as tmp:
            content, preview, title, description, note = validate_zip_and_copy(
                args.zip, args.checkout, Path(tmp))
            raw = make_vdf(content, preview, title, description, note, EXPECTED_WORKSHOP_ID)
            if '"visibility"' in raw:
                raise ValueError('Existing-item VDF must not set Workshop visibility')
            tags = workshop_tags(ET.fromstring((content / 'About/About.xml').read_bytes()))
            if note not in raw:
                raise ValueError('Complete changenote was not staged')
            print('Offline visibility-preserving existing-item VDF and source ZIP PASS; NO UPLOAD')
            print('Expected Workshop tags (Steamworks step required): ' + ', '.join(tags))
            print('Existing public Workshop ID: ' + EXPECTED_WORKSHOP_ID + ' (creation disabled; visibility unchanged)')
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
