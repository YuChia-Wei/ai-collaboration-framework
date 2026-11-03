"""Build the release's native templates and self-contained snippet tools."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def build(repository, output, work, version, commit):
    if output.exists() or work.exists():
        raise ValueError('Choose fresh build/output directories')
    actual = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != commit:
        raise ValueError('Generation source commit mismatch')
    generation = repository / 'src/knowledge/dotnet-backend/tooling/generation'
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    subprocess.run(['dotnet', 'pack', str(generation / 'Generation.Templates.csproj'),
                    '-c', 'Release', '-o', str(output / 'templates'),
                    '--artifacts-path', str(work / 'templates'), '-p:PackageVersion=' + version], check=True)
    for rid in ('win-x64', 'linux-x64'):
        subprocess.run(['dotnet', 'publish', str(generation / 'snippet-tool/SnippetTool.csproj'),
                        '-c', 'Release', '-r', rid, '--self-contained', 'true',
                        '--artifacts-path', str(work / rid), '-o', str(output / 'snippets' / rid),
                        '-p:Version=' + version, '-p:PublishAot=false', '-p:PublishSingleFile=true',
                        '-p:IncludeNativeLibrariesForSelfExtract=true', '-p:DebugType=None',
                        '-p:DebugSymbols=false'], check=True)
    shutil.copyfile(repository / 'src/tools/install-generation.py', output / 'install-generation.py')
    shutil.copyfile(generation / 'DELIVERY.md', output / 'README.md')
    shutil.copyfile(generation / 'snippet-tool/README.md', output / 'snippets/README.md')
    rows = []
    for path in sorted(output.rglob('*')):
        if path.is_file():
            name = path.relative_to(output).as_posix()
            mode = 0o755 if name == 'snippets/linux-x64/SnippetTool' else 0o644
            rows.append(dict(path=name, size=path.stat().st_size,
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(), mode=mode))
    manifest = dict(schema='aicf-generation/1', source_commit=commit, version=version,
                    runtimes=['win-x64', 'linux-x64'], mode='self-contained-coreclr-single-file', files=rows)
    (output / 'generation.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'output', 'work'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--version', required=True)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    build(args.repository.resolve(), args.output.resolve(), args.work.resolve(), args.version, args.commit)
