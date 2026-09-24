"""Issue #403 direct content checks only; no framework/behavioral validation."""
import collections
import hashlib
import json
import pathlib
import posixpath
import re
import stat
import subprocess
import yaml

ROOT = pathlib.Path.cwd()
CONTRACT = ROOT / '.dev/design/framework-next/rc2-contracts'
WORKFLOW = ROOT / '.dev/workflows/2026-09-24-rc2-engineering-knowledge'
PACKAGE_ROOT = ROOT / 'src/knowledge'


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes().decode('utf-8'))


def read_yaml(path):
    return yaml.safe_load(path.read_bytes().decode('utf-8'))


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


plan = read_json(CONTRACT / 'package-members.json')
inventory = read_json(CONTRACT / 'migration-inventory.json')
source_edges = read_json(CONTRACT / 'reference-dispositions.json')['edges']
handoff = read_json(WORKFLOW / 's3-package-handoff.json')
reconciliation = read_json(WORKFLOW / 'evidence/reference-reconciliation.json')['edges']
normative = read_json(WORKFLOW / 'evidence/normative-rewrites.json')['rules']
source_rows = {x['source']['path']: x for x in inventory['files']}
source_tree = subprocess.check_output(['git', 'ls-tree', '-r', inventory['source_commit']], cwd=ROOT).decode('utf-8')
tree_rows = {}
for line in source_tree.splitlines():
    identity, path = line.split('\t', 1)
    mode, kind, blob = identity.split()
    tree_rows[path] = (mode, kind, blob)
source_stream = subprocess.run(['git', 'cat-file', '--batch'], input=('\n'.join(x['source']['git_blob'] for x in inventory['files']) + '\n').encode(), stdout=subprocess.PIPE, check=True, cwd=ROOT).stdout
cursor = 0
sources = {}
for row in inventory['files']:
    source = row['source']
    require(tree_rows[source['path']] == (source['mode'], 'blob', source['git_blob']), 'Source path/blob/mode mismatch: ' + source['path'])
    end = source_stream.index(b'\n', cursor)
    length = int(source_stream[cursor:end].split()[2])
    cursor = end + 1
    raw = source_stream[cursor:cursor + length]
    cursor += length + 1
    require(len(raw) == source['size'] and digest(raw) == source['sha256'], 'Source bytes mismatch: ' + source['path'])
    sources[source['path']] = raw

require(len(reconciliation) == len(source_edges) == 381, 'Incomplete source-edge reconciliation')
for original, final in zip(source_edges, reconciliation):
    require(all(final[k] == v for k, v in original.items()), 'Source edge identity changed')
    require(bool(final['actual_disposition']), 'Missing edge disposition')

metadata = {p['id']: read_yaml(PACKAGE_ROOT / p['id'] / 'content-package.yaml') for p in plan['packages']}
resources = {k: {r['id']: r for r in v['resources']} for k, v in metadata.items()}
links_checked = 0
parsed = collections.Counter()
member_counts = {}
link_pattern = re.compile(r'(?<!!)\[([^\]\n]*)\]\(([^)\s]+)\)')
for package, package_handoff in zip(plan['packages'], handoff['packages']):
    package_id = package['id']
    base = PACKAGE_ROOT / package_id
    meta = metadata[package_id]
    expected = {m['path']: m for m in package['members']}
    actual = {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
    require(actual == set(expected), 'Package member set differs: ' + package_id)
    require(len({x.casefold() for x in actual}) == len(actual), 'Case alias collision')
    require(meta['members'] == [{'path': m['path'], 'kind': m['kind']} for m in package['members']], 'Metadata member projection differs')
    require(meta['dependencies'] == package['dependencies'], 'Dependency changed')
    require(meta['content_package_version'] == 1 and type(meta['content_package_version']) is int, 'Metadata version differs')
    require(set(meta) == {'content_package_version', 'id', 'version', 'entrypoint', 'members', 'resources', 'dependencies', 'references'}, 'Unexpected metadata fields')
    require((base / 'content-package.yaml').stat().st_size <= 256 * 1024, 'Source YAML size cap exceeded')
    require(len(meta['resources']) == len(resources[package_id]), 'Duplicate resource ID')
    for r in meta['resources']:
        require(r['path'] in expected, 'Resource outside member closure')
    for key in ['resources', 'references', 'entrypoint']:
        require(package_handoff[key] == meta[key], 'Handoff differs: ' + key)
    for r in meta['references']:
        require(r['from'] in expected, 'Reference source missing')
        target = r['target']
        require(r['resource_id'] in resources[target['package']], 'Missing target resource')
        require(resources[target['package']][r['resource_id']]['path'] == target['path'], 'Target resource/member mismatch')
        if target['package'] != package_id:
            require({'kind': 'knowledge', 'id': target['package'], 'version': '0.1.0'} in meta['dependencies']['required'], 'Missing required package dependency')
    sorted_references = sorted(meta['references'], key=lambda r: (r['from'], r['resource_id'], r['target']['package'], r['target']['path'], r['target']['anchor'] or ''))
    require(sorted_references == meta['references'], 'Unsorted references')
    require(len({json.dumps(x, sort_keys=True) for x in meta['references']}) == len(meta['references']), 'Duplicate reference')
    rows = {x['path']: x for x in package_handoff['members']}
    require(set(rows) == actual, 'Handoff member set differs')
    for name in sorted(actual):
        f = base / name
        require(stat.S_ISREG(f.lstat().st_mode) and not f.is_symlink(), 'Non-regular member')
        raw = f.read_bytes()
        require(not raw.startswith(b'\xef\xbb\xbf'), 'Unexpected BOM')
        text = raw.decode('utf-8')
        require(rows[name]['sha256'] == digest(raw) and rows[name]['size'] == len(raw), 'Handoff hash/size mismatch: ' + name)
        source = expected[name]['source_ref']
        require(rows[name]['source_identity'] == (source_rows[source]['source'] if source else None), 'Source identity changed')
        require(rows[name]['mode'] == (source_rows[source]['source']['mode'] if source else '100644'), 'Mode changed')
        parsed['utf8'] += 1
        if f.suffix.lower() in ['.yaml', '.yml']:
            yaml.safe_load(text)
            parsed['yaml'] += 1
        if f.suffix.lower() == '.json':
            json.loads(text)
            parsed['json'] += 1
        if name.endswith('/sub-agent.yaml'):
            projection = yaml.safe_load(text)
            require(projection['content_kind'] == 'reference-only-technical-guidance', 'Active role projection')
            require(not set(projection) & {'asset_type', 'triggers', 'routing', 'wrapper_targets', 'adapter_metadata', 'workflow', 'role_kind', 'status'}, 'Runtime activation field')
        if f.suffix.lower() != '.md':
            continue
        plain = re.sub(r'```.*?```|~~~.*?~~~', '', text, flags=re.S)
        require('.ai/assets' not in plain and '.ai/scripts' not in plain, 'Active source-checkout reference: ' + name)
        for label, url in link_pattern.findall(plain):
            if re.match(r'^[a-zA-Z]+://|mailto:', url):
                continue
            target_path, _, anchor = url.partition('#')
            target_name = posixpath.normpath(posixpath.join(package_id, posixpath.dirname(name), target_path)) if target_path else package_id + '/' + name
            target_package, _, target_member = target_name.partition('/')
            require(target_package in metadata and target_member in {m['path'] for m in metadata[target_package]['members']}, 'Unresolved installed link: ' + name + ' -> ' + url)
            target_file = PACKAGE_ROOT / target_package / target_member
            if anchor:
                headings = re.findall(r'^#{1,6}\s+(.+?)\s*#*$', target_file.read_text(encoding='utf-8'), re.M)
                slugs = [re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-') for heading in headings]
                require(anchor in slugs, 'Missing heading anchor: ' + url)
            require(any(r['from'] == name and r['target'] == {'package': target_package, 'path': target_member, 'anchor': anchor or None} for r in meta['references']), 'Undeclared Markdown reference: ' + name + ' -> ' + url)
            links_checked += 1
    member_counts[package_id] = len(actual)

rules = []
for package_id in metadata:
    catalog = read_yaml(PACKAGE_ROOT / package_id / 'engineering-rule-catalog.yaml')
    catalog_input = {k: v for k, v in catalog.items() if k != 'catalog_digest'}
    require(catalog['catalog_digest']['value'] == digest(json.dumps(catalog_input, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'), 'Catalog digest mismatch')
    for rule in catalog['rules']:
        prior = next(x for x in inventory['rules'] if x['rule_id'] == rule['rule_id'])
        old_catalog = yaml.safe_load(sources[prior['catalog_source']['path']])
        old_rule = next(x for x in old_catalog['rules'] if x['rule_id'] == rule['rule_id'])
        for field in ['rule_id', 'domain', 'strength', 'scope', 'applicability', 'override_policy', 'decision_evidence', 'status']:
            require(rule[field] == old_rule[field], 'Rule authority field changed: ' + rule['rule_id'] + '/' + field)
        require(digest(old_rule['normative_text']) == prior['normative_text_sha256'], 'Source normative digest differs')
        require(digest(rule['normative_text']) == rule['normative_text_sha256'], 'Installed normative digest differs')
        norm = next(x for x in normative if x['rule_id'] == rule['rule_id'])
        transformed = old_rule['normative_text']
        # Substitutions are exact text changes, not a new normative statement.
        for rewrite in norm['link_rewrites'] + norm['target_parameter_rewrites']:
            transformed = transformed.replace(rewrite['before'], rewrite['after'])
        require(transformed == rule['normative_text'], 'Unexplained normative text delta: ' + rule['rule_id'])
        if package_id == 'dotnet-backend':
            owner = PACKAGE_ROOT / package_id / rule['semantic_owner']['path']
            require(digest(owner.read_bytes()) == rule['source_file_sha256'], 'Relocated owner hash differs')
            owner_text = owner.read_text(encoding='utf-8')
            anchor = rule['semantic_owner']['anchor']
            remainder = owner_text[owner_text.index(anchor + '\n'):].splitlines(True)
            level = len(anchor) - len(anchor.lstrip('#'))
            lines = []
            for index, line in enumerate(remainder):
                if index and re.match(r'^#{1,' + str(level) + r'}\s', line):
                    break
                lines.append(line if line.strip() else '\n')
            require(''.join(lines).rstrip() + '\n' == rule['normative_text'], 'Projection differs from Markdown owner: ' + rule['rule_id'])
        rules.append(rule['rule_id'])
    for item in catalog.get('unpacketized_documents', []):
        member = item['canonical_source']['path']
        require(item['source_file_sha256'] == digest((PACKAGE_ROOT / package_id / member).read_bytes()), 'Guidance hash mismatch')
        require(item['packet_state'] == 'identity-allocation-required' and 'rule_id' not in item, 'Invented guidance rule identity')
require(sorted(rules) == sorted(x['rule_id'] for x in inventory['rules']) and len(set(rules)) == 14, 'Rule identity set changed')
profile_rows = [x for x in inventory['files'] if x['source']['path'].startswith('.ai/assets/tech-stacks/dotnet-backend/')]
require(len(profile_rows) == 194, 'Profile inventory incomplete')
print(json.dumps({'check_kind': 'direct-static-content-comparison', 'schema_compliance_claim': False, 'behavioral_execution': 'deferred-by-owner', 'source_identities': len(sources), 'members': member_counts, 'profile_dispositions': dict(collections.Counter(x['classification'] for x in profile_rows)), 'source_edges': len(reconciliation), 'declared_references': {k: len(v['references']) for k, v in metadata.items()}, 'markdown_links': links_checked, 'parsed_files': dict(parsed), 'registered_rules': len(rules), 'unregistered_guidance': 11, 'result': 'passed'}, indent=2))
