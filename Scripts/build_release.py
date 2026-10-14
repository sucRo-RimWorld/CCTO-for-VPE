#!/usr/bin/env python3
"""Deterministic source-only subscriber ZIP; does not upload to Steam."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    'About/About.xml', 'About/Manifest.xml', 'About/Changelog.txt',
    'About/PublishedFileId.txt', 'About/Preview.png',
    'Patches/ColdTolerance.xml', 'LICENSE',
)
FOLDER = 'CCTO-for-VPE/'
DATE = (2026, 10, 13, 0, 0, 0)
EXPECTED_WORKSHOP_ID = '3819497323'  # Author-selected existing item; never auto-create a replacement


def check_preview(data: bytes) -> None:
    """PNG framing, CRCs, complete image decompression, and approved dimensions."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Invalid preview PNG signature')
    offset, chunks, ihdr, ended = 8, [], None, False
    while offset + 12 <= len(data):
        n = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset+4:offset+8]
        end = offset + 12 + n
        if end > len(data):
            raise ValueError('Truncated PNG chunk')
        content = data[offset+8:offset+8+n]
        crc = struct.unpack_from('>I', data, offset+8+n)[0]
        if zlib.crc32(kind + content) & 0xffffffff != crc:
            raise ValueError('PNG chunk CRC mismatch')
        if kind == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', content)
        if kind == b'IDAT':
            chunks.append(content)
        offset = end
        if kind == b'IEND':
            ended = offset == len(data)
            break
    if not ended or not chunks or ihdr != (640, 360, 8, 3, 0, 0, 0):
        raise ValueError('Missing PNG data or unexpected preview size/format')
    if len(zlib.decompress(b''.join(chunks))) != 360 * (1 + 640):
        raise ValueError('Malformed or incomplete decoded preview')


def validate(root: Path = ROOT) -> dict[str, bytes]:
    files = {}
    for path in FILES:
        src = root / path
        if not src.is_file():
            raise ValueError('Missing subscriber file: ' + path)
        files[path] = src.read_bytes()
    source_manifest = json.loads((root / 'Docs/ApprovedPreview.json').read_text(encoding='utf-8'))
    src = root / source_manifest['source']['repository_path']
    if hashlib.sha256(src.read_bytes()).hexdigest() != source_manifest['source']['sha256']:
        raise ValueError('Approved high-resolution source has changed')
    if hashlib.sha256(files['About/Preview.png']).hexdigest() != source_manifest['preview']['sha256']:
        raise ValueError('Preview differs from author-approved resized image')
    check_preview(files['About/Preview.png'])
    published_id = files['About/PublishedFileId.txt'].decode('utf-8').strip()
    if published_id != EXPECTED_WORKSHOP_ID:
        raise ValueError('PublishedFileId.txt does not match the author-selected existing Workshop item')
    about = ET.fromstring(files['About/About.xml'])
    manifest = ET.fromstring(files['About/Manifest.xml'])
    version = about.findtext('modVersion')
    if not version or not re.fullmatch(r'\d+\.\d+\.\d+(?:\.\d+)?', version):
        raise ValueError('Invalid addon version')
    if manifest.findtext('version') != version:
        raise ValueError('About / Manifest version mismatch')
    if about.findtext('packageId') != 'sucro.cctoforvpe':
        raise ValueError('Changed addon packageId')
    if [x.text for x in about.findall('./supportedVersions/li')] != ['1.6']:
        raise ValueError('Unreviewed RimWorld supported version')
    deps = {x.findtext('packageId') for x in about.findall('./modDependencies/li')}
    if deps != {'sucro.cropcoldtoleranceoverhaul', 'VanillaExpanded.VPlantsE'}:
        raise ValueError('Wrong dependencies or unsupported packs made mandatory')
    headings = [line for line in files['About/Changelog.txt'].decode().splitlines()
                if re.match(r'^\d+\.\d+\.\d+', line)]
    if len(headings) != 1 or not headings[0].startswith(version + ' - '):
        raise ValueError('Changelog heading differs from current version')
    if ET.fromstring(files['Patches/ColdTolerance.xml']).tag != 'Patch':
        raise ValueError('Invalid production XML')
    return files


def check_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        if sorted(archive.namelist()) != sorted(FOLDER + item for item in FILES):
            raise ValueError('Subscriber ZIP content differs from exact reviewed allowlist')
        if archive.testzip() is not None:
            raise ValueError('ZIP CRC mismatch')
        check_preview(archive.read(FOLDER + 'About/Preview.png'))


def create_zip(output: Path, source: Path = ROOT) -> Path:
    files = validate(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=9) as archive:
        for path, data in files.items():
            info = zipfile.ZipInfo(FOLDER + path, date_time=DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=9)
    check_zip(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'Dist/CCTO-for-VPE-0.1.0.zip')
    args = parser.parse_args()
    path = create_zip(args.output)
    print(f'[OK] Subscriber-only deterministic ZIP: {path} ({path.stat().st_size} bytes)')
    print('File inventory:', ', '.join(FILES))
    print('Evidence: package/source-level only; RimWorld runtime / Steam upload NOT verified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
