"""Versioned standalone download names and their verified source paths."""
from io import BytesIO
import stat
import zipfile


def tool_asset_sources(version):
    return {
        f'SnippetTool-{version}-win-x64.exe': 'generation/snippets/win-x64/SnippetTool.exe',
        f'SnippetTool-{version}-linux-x64': 'generation/snippets/linux-x64/SnippetTool',
        f'RefactorTool-{version}-win-x64.exe': 'RefactorTool.exe',
        f'RefactorTool-{version}-win-x64-notices.zip': None,
    }


def verify_notices_names(names):
    required = {'README.md', 'THIRD-PARTY-NOTICES.txt'}
    if not required <= names or not names - required or any(
            not name.startswith('licenses/') for name in names - required):
        raise ValueError('RefactorTool notices inventory mismatch')


def refactor_notices(files):
    verify_notices_names(set(files))
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, raw, compress_type=zipfile.ZIP_DEFLATED)
    return buffer.getvalue()
