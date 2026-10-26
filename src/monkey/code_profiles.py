"""Built-in, exact-source typed C# recovery profiles."""
from __future__ import annotations

import re
from importlib.resources import files
from pathlib import Path

from .io import encoded, load, read, safe, sha
from .sources.compiled import fail

_PROFILES = {
    'foodstreet-demand-health-v1': ('code_profiles', 'foodstreet-demand-health-v1.json'),
}
_MAX_PROFILE_BYTES = 128 * 1024
_MAX_SOURCE_BYTES = 16 * 1024 * 1024
_HEX = re.compile(r'[0-9a-f]{64}\Z')


def load_profile(profile_name: str, source_path) -> bytes:
    """Return canonical UTF-8 JSON bytes for a built-in profile.

    The source must match the bundled whole-file SHA-256 and byte length. The
    returned bytes contain only typed contracts and source identities, never
    original source code or private workspace paths.
    """
    if not isinstance(profile_name, str) or profile_name not in _PROFILES:
        fail('CODE_PROFILE_UNKNOWN', str(profile_name), 'Unknown built-in profile name')
    package_parts = _PROFILES[profile_name]
    resource = files('monkey').joinpath(*package_parts)
    profile_raw = resource.read_bytes()
    if len(profile_raw) > _MAX_PROFILE_BYTES:
        fail('CODE_PROFILE_BUDGET', profile_name, 'Bundled profile exceeds size limit')
    profile = load(profile_raw, max_nodes=20_000, max_depth=48)
    if encoded(profile) != profile_raw:
        fail('CODE_PROFILE_CANONICAL', profile_name, 'Bundled profile is not canonical JSON')
    if profile.get('profileName') != profile_name or profile.get('schemaVersion') != 1:
        fail('CODE_PROFILE_SCHEMA', profile_name, 'Profile identity or schema version mismatch')
    expected_sha = profile.get('sourceSha256')
    expected_bytes = profile.get('sourceBytes')
    if not isinstance(expected_sha, str) or not _HEX.fullmatch(expected_sha) or \
       type(expected_bytes) is not int or not 0 < expected_bytes <= _MAX_SOURCE_BYTES:
        fail('CODE_PROFILE_SCHEMA', profile_name, 'Invalid pinned source identity')
    source = safe(Path(source_path))
    source_raw = read(source, max_bytes=_MAX_SOURCE_BYTES)
    if len(source_raw) != expected_bytes or sha(source_raw) != expected_sha:
        fail('CODE_PROFILE_SOURCE_IDENTITY', str(source), 'Source bytes do not match the selected exact profile')
    return encoded(profile)
