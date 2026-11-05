"""Build and admit platform-native tool outputs for one immutable source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess

RUNTIMES = {'win-x64': ('Windows', 'AMD64', ('snippets', 'formatting')),
            'linux-x64': ('Linux', 'x86_64', ('snippets',)),
            'osx-arm64': ('Darwin', 'arm64', ('formatting',))}
PROJECTS = {'snippets': 'generation/snippet-tool/SnippetTool.csproj',
            'formatting': 'formatting/FormatTool.csproj'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(repository, output, work, version, commit, rid):
    system, machine, selected = RUNTIMES[rid]
    if platform.system() != system or platform.machine().lower() != machine.lower():
        raise ValueError('Native AOT requires the selected OS/architecture runner')
    if subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip() != commit:
        raise ValueError('Native source commit mismatch')
    if subprocess.check_output(['git', '-C', str(repository), 'status', '--porcelain', '--untracked-files=all']):
        raise ValueError('Clean native source checkout required')
    if output.exists() or work.exists():
        raise ValueError('Choose fresh native output/work directories')
    output.mkdir(parents=True)
    work.mkdir(parents=True)
    environment = {k: v for k, v in os.environ.items()
                   if not any(x in k.upper() for x in ('TOKEN', 'SECRET', 'PASSWORD', 'CREDENTIAL'))}
    for tool in selected:
        project = repository / 'src/knowledge/dotnet-backend/tooling' / PROJECTS[tool]
        subprocess.run(['dotnet', 'publish', str(project), '-c', 'Release', '-r', rid,
                        '--self-contained', 'true', '-p:PublishAot=true', '-p:PublishSingleFile=false',
                        '-p:DebugType=None', '-p:DebugSymbols=false', '-p:StripSymbols=true',
                        '-p:CopyOutputSymbolsToPublishDirectory=false',
                        '-p:Version=' + version, '--artifacts-path', str(work / tool),
                        '-o', str(output / tool / rid)], check=True, env=environment)
    if subprocess.check_output(['git', '-C', str(repository), 'status', '--porcelain', '--untracked-files=all']):
        raise ValueError('Source drift during native build')
    rows = [dict(path=p.relative_to(output).as_posix(), size=p.stat().st_size, sha256=digest(p))
            for p in sorted(output.rglob('*')) if p.is_file()]
    manifest = dict(schema='aicf-native-tools/1', source_commit=commit, version=version, rid=rid, files=rows)
    (output / 'native-tools.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


def collect(root, output, version, commit):
    """Require all native runners' exact source/version and hash every input."""
    # The caller's root may use an OS alias such as macOS /tmp -> /private/tmp.
    # Links inside the artifact boundary remain forbidden.
    root = root.resolve()
    missing = ('Missing native runtime artifacts for this run attempt; '
               'rerun all native jobs and the bundle build together')
    if not root.is_dir():
        raise ValueError(missing)
    seen = set()
    for directory in sorted(root.iterdir()):
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError('Expected one native artifact directory per runtime')
        manifest = json.loads((directory / 'native-tools.json').read_text(encoding='utf-8'))
        rid = manifest['rid']
        if (manifest['schema'] != 'aicf-native-tools/1' or manifest['source_commit'] != commit
                or manifest['version'] != version or rid not in RUNTIMES or rid in seen):
            raise ValueError('Native artifact source/version/runtime mismatch')
        seen.add(rid)
        expected = {'native-tools.json'}
        for row in manifest['files']:
            name = row['path']
            parts = name.split('/')
            if (len(parts) < 3 or parts[0] not in RUNTIMES[rid][2] or parts[1] != rid
                    or any(p in ('', '.', '..') for p in parts) or '\\' in name or ':' in name
                    or name in expected):
                raise ValueError('Invalid native artifact member')
            expected.add(name)
            path = directory / name
            if not path.is_file() or any((root / p).is_symlink()
                                        for p in (path.relative_to(root), *path.relative_to(root).parents)):
                raise ValueError('Native artifact member hash/type mismatch')
            raw = path.read_bytes()
            if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                raise ValueError('Native artifact member hash/type mismatch')
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
        if actual != expected or any(p.is_symlink() for p in directory.rglob('*')):
            raise ValueError('Native artifact inventory mismatch')
    if seen != set(RUNTIMES):
        raise ValueError(missing)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'output', 'work'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('version', 'commit'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--rid', choices=RUNTIMES, required=True)
    args = parser.parse_args()
    build(args.repository.resolve(), args.output.resolve(), args.work.resolve(), args.version, args.commit, args.rid)
