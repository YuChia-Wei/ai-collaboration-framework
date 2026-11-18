"""Build native templates, snippets and formatting in the existing tool bundle."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).absolute().parent))
from native_tools import collect
from release_common import LEGACY_SNIPPET_RIDS, source_snippet_rids


def build(repository, output, work, version, commit, native_tools=None, coreclr=False, refactor_output=None):
    if (native_tools is None) == (not coreclr):
        raise ValueError('Select native artifacts or explicit CoreCLR comparison')
    if output.exists() or work.exists():
        raise ValueError('Choose fresh build/output directories')
    actual = subprocess.check_output(['git', '-C', str(repository), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != commit:
        raise ValueError('Generation source commit mismatch')
    runtimes = LEGACY_SNIPPET_RIDS if coreclr else source_snippet_rids(repository, commit)
    generation = repository / 'src/tools/dotnet/generation'
    guides = repository / 'src/knowledge/dotnet/tooling/generation'
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    subprocess.run(['dotnet', 'pack', str(generation / 'Generation.Templates.csproj'),
                    '-c', 'Release', '-o', str(output / 'templates'),
                    '--artifacts-path', str(work / 'templates'), '-p:PackageVersion=' + version], check=True)
    publications = [(generation / 'snippet-tool/SnippetTool.csproj', 'snippets', rid)
                    for rid in LEGACY_SNIPPET_RIDS]
    for project, tool, rid in publications if coreclr else []:
        subprocess.run(['dotnet', 'publish', str(project),
                        '-c', 'Release', '-r', rid, '--self-contained', 'false',
                        '--artifacts-path', str(work / tool / rid), '-o', str(output / tool / rid),
                        '-p:Version=' + version, '-p:PublishAot=false', '-p:PublishSingleFile=true',
                        '-p:DebugType=None',
                        '-p:DebugSymbols=false'], check=True)
    if native_tools is not None:
        collect(native_tools, output, version, commit, refactor_output, runtimes=runtimes)
    shutil.copyfile(repository / 'src/tools/install-generation.py', output / 'install-generation.py')
    shutil.copyfile(guides / 'DELIVERY.md', output / 'README.md')
    shutil.copyfile(guides / 'snippet-tool/README.md', output / 'snippets/README.md')
    (output / 'formatting').mkdir()
    for name in ('Format-Dotnet.ps1', 'README.md'):
        shutil.copyfile(generation.parent / 'formatting' / name, output / 'formatting' / name)
    executables = {f'snippets/{rid}/SnippetTool' for rid in runtimes if rid != 'win-x64'}
    rows = []
    for path in sorted(output.rglob('*')):
        if path.is_file():
            name = path.relative_to(output).as_posix()
            mode = 0o755 if name in executables else 0o644
            rows.append(dict(path=name, size=path.stat().st_size,
                             sha256=hashlib.sha256(path.read_bytes()).hexdigest(), mode=mode))
    manifest = dict(schema='aicf-generation/1', source_commit=commit, version=version,
                    formatting={'kind': 'dotnet-format-script'},
                    runtimes=list(runtimes),
                    mode='framework-dependent-coreclr-single-file' if coreclr else 'native-aot', files=rows)
    (output / 'generation.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repository', 'output', 'work'):
        parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--version', required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--native-tools', type=Path)
    parser.add_argument('--coreclr', action='store_true', help='Explicit framework-dependent comparison build')
    parser.add_argument('--refactor-output', type=Path)
    args = parser.parse_args()
    build(args.repository.resolve(), args.output.resolve(), args.work.resolve(), args.version, args.commit,
          args.native_tools, args.coreclr, args.refactor_output)
