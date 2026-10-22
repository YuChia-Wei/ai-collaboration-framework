"""Project-owned model policy; no model calls, installation or native-config writes.

Selection is a proposal for a caller-controlled invocation, not a budget enforcer.
Policy operations write only POLICY_PATH. The public dispatcher delegates explicit
resource operations to subagent_registry; neither writer edits the framework lock.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import tempfile

POLICY_PATH = '.ai/custom/sub-agent-policy.json'
LIMIT = 256 * 1024
TIERS = ('routine', 'reasoning', 'premium')
TASKS = {'inventory': 'routine', 'translation': 'routine', 'synthesis': 'routine',
         'implementation': 'reasoning', 'semantic-review': 'reasoning',
         'independent-review': 'reasoning'}


class PolicyError(ValueError):
    pass


def require(value, message):
    if not value:
        raise PolicyError(message)


def pairs(rows):
    result = {}
    for key, value in rows:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def decode(raw):
    require(len(raw) <= LIMIT, 'policy document budget')
    def invalid(_):
        raise PolicyError('unsupported JSON scalar')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=invalid, parse_float=invalid)


def defaults():
    """Explicit initialization proposal; never an implicit fallback for a missing file."""
    return {'schema_version': 1, 'on_unavailable': 'stop', 'tasks': dict(TASKS),
            'adapters': {
                'codex': {'routine': {'model': 'gpt-6-luna', 'effort': 'medium'},
                          'reasoning': {'model': 'gpt-6.1-sol', 'effort': 'medium'},
                          'premium': {'model': 'gpt-6-astra', 'effort': 'low'}},
                'claude': {'routine': {'model': 'haiku', 'effort': None},
                           'reasoning': {'model': 'sonnet', 'effort': 'medium'},
                           'premium': {'model': 'opus', 'effort': 'medium'}}},
            'extensions': {}}


def validate(value):
    require(type(value) is dict and set(value) == {
        'schema_version', 'on_unavailable', 'tasks', 'adapters', 'extensions'}, 'policy fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'policy version')
    require(value['on_unavailable'] == 'stop', 'parent fallback is unsupported')
    require(type(value['extensions']) is dict, 'extensions must be an object')
    require(type(value['tasks']) is dict and value['tasks'], 'task mapping required')
    for task, tier in value['tasks'].items():
        require(re.fullmatch(r'[a-z][a-z0-9-]{0,63}', task) and tier in TIERS, 'task mapping')
    require(type(value['adapters']) is dict and set(value['adapters']) == {'codex', 'claude'}, 'adapter closure')
    for adapter, tiers in value['adapters'].items():
        require(type(tiers) is dict and set(tiers) == set(TIERS), 'tier closure')
        models = []
        for tier, choice in tiers.items():
            require(type(choice) is dict and set(choice) == {'model', 'effort'}, 'choice fields')
            model, effort = choice['model'], choice['effort']
            require(type(model) is str and re.fullmatch(r'[a-zA-Z0-9_.:-]{1,128}', model), 'model identifier')
            require(model not in {'inherit', 'default', 'opusplan'}, 'implicit model selection denied')
            require(model.startswith('gpt-') if adapter == 'codex' else
                    model in {'haiku', 'sonnet', 'opus'} or model.startswith('claude-'), 'provider boundary')
            require(effort in ({'low', 'medium', 'high', 'xhigh', 'max', 'ultra'} if adapter == 'codex'
                               else {None, 'low', 'medium', 'high', 'max'}), 'unsupported effort')
            # Custom future IDs require owner classification; known premium families cannot be demoted.
            require(tier == 'premium' or not re.search(r'astra|opus', model, re.I), 'premium model in ordinary tier')
            models.append(model)
        require(len(set(models)) == 3, 'tiers must use distinct models')
    # A proposal must be readable after apply, including extension values.
    require(decode(encode(value)) == value, 'policy JSON round trip')
    return value


def direct(target, *, directory=False, missing=False):
    require(target.is_absolute() and '..' not in target.parts, 'absolute direct path required')
    for part in reversed((target, *target.parents)):
        if part.parent != part and part.parent.is_dir():
            matches = [p.name for p in part.parent.iterdir() if p.name.casefold() == part.name.casefold()]
            require(matches in ([], [part.name]), 'policy path case collision')
        try:
            info = part.lstat()
        except FileNotFoundError:
            require(missing, 'required path missing')
            continue
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400,
                'linked policy path')
        if part != target or directory:
            require(stat.S_ISDIR(info.st_mode), 'policy ancestor must be directory')
        else:
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= LIMIT,
                    'policy file type or budget')


def location(project):
    root = Path(project)
    direct(root, directory=True)
    target = root / POLICY_PATH
    direct(target, missing=True)
    return target


def raw_read(target):
    direct(target, missing=True)
    if not target.exists():
        return None
    before = target.stat()
    with target.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(LIMIT + 1)
        after = os.fstat(stream.fileno())
    final = target.stat()
    signature = lambda row: (row.st_dev, row.st_ino, row.st_size, row.st_mtime_ns, row.st_nlink)
    require(signature(before) == signature(opened) == signature(after) == signature(final), 'policy read drift')
    require(len(raw) <= LIMIT, 'policy document budget')
    return raw


def digest(raw):
    return None if raw is None else sha256(raw).hexdigest()


def inspect(project):
    raw = raw_read(location(project))
    return {'outcome': 'missing' if raw is None else 'inspected', 'changed': False,
            'path': POLICY_PATH, 'sha256': digest(raw),
            'policy': None if raw is None else validate(decode(raw)),
            'ownership': 'project', 'invocation_observed': False}


def native_defaults(policy):
    return {'codex': {'agents': {
        'default_subagent_model': policy['adapters']['codex']['routine']['model'],
        'default_subagent_reasoning_effort': policy['adapters']['codex']['routine']['effort']}},
        'claude': {'env': {'CLAUDE_CODE_SUBAGENT_MODEL': policy['adapters']['claude']['routine']['model']}}}


def plan(project, proposed):
    validate(proposed)
    current = inspect(project)
    document = {'plan_version': 1, 'project_root': str(Path(project)), 'path': POLICY_PATH,
                'before_sha256': current['sha256'], 'after_sha256': digest(encode(proposed)),
                'proposed': deepcopy(proposed)}
    return {'outcome': 'planned', 'changed': False, 'plan': document,
            'plan_sha256': digest(encode(document)), 'native_settings_proposal': native_defaults(proposed)}


def apply(project, document, plan_sha256):
    require(type(document) is dict and set(document) == {
        'plan_version', 'project_root', 'path', 'before_sha256', 'after_sha256', 'proposed'}, 'plan fields')
    require(document['plan_version'] == 1 and document['path'] == POLICY_PATH
            and document['project_root'] == str(Path(project)), 'plan target')
    require(digest(encode(document)) == plan_sha256, 'plan changed')
    validate(document['proposed'])
    replacement = encode(document['proposed'])
    require(digest(replacement) == document['after_sha256'], 'plan content changed')
    target = location(project)
    # Validate all existing ancestors before creating only this policy's parent.
    target.parent.mkdir(parents=True, exist_ok=True)
    direct(target.parent, directory=True)
    guard = target.with_suffix('.json.writer')
    try:
        guard_fd = os.open(guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise PolicyError('policy writer active; preserve existing guard and reconcile its owner')
    temporary = None
    try:
        os.close(guard_fd)
        current = raw_read(target)
        if current == replacement:
            return {'outcome': 'unchanged', 'changed': False, 'sha256': digest(current)}
        require(digest(current) == document['before_sha256'], 'stale policy plan')
        fd, name = tempfile.mkstemp(prefix='.sub-agent-policy-', dir=target.parent)
        temporary = Path(name)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(replacement)
            stream.flush()
            os.fsync(stream.fileno())
        require(digest(raw_read(target)) == document['before_sha256'], 'policy changed before replacement')
        os.replace(temporary, target)
        temporary = None
        require(raw_read(target) == replacement, 'policy readback mismatch')
        return {'outcome': 'applied', 'changed': True, 'path': POLICY_PATH, 'sha256': digest(replacement),
                'native_settings_applied': False, 'invocation_observed': False}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        guard.unlink()


def compare(baseline, local, candidate):
    validate(local)
    validate(candidate)
    if baseline is None:
        return {'outcome': 'baseline-unavailable', 'changed': False,
                'semantic_coverage': 'unknown', 'adoption': 'unknown', 'activation': 'unknown'}
    validate(baseline)
    missing = object()
    rows = []
    def visit(base, current, incoming, path=''):
        if all(type(v) is dict for v in (base, current, incoming)):
            for key in sorted(set(base) | set(current) | set(incoming)):
                visit(base.get(key, missing), current.get(key, missing), incoming.get(key, missing), path + '/' + key)
        elif current != base or incoming != base:
            disposition = ('same-change' if current == incoming else 'candidate-only' if current == base
                           else 'local-only' if incoming == base else 'conflict')
            rows.append({'path': path, 'difference': disposition,
                         'baseline': None if base is missing else base,
                         'local': None if current is missing else current,
                         'candidate': None if incoming is missing else incoming})
    visit(baseline, local, candidate)
    return {'outcome': 'compared', 'changed': False, 'differences': rows,
            'semantic_coverage': 'unknown', 'adoption': 'unknown', 'activation': 'unknown'}


def version_at_least(value, minimum):
    require(type(value) is str and re.fullmatch(r'\d+\.\d+\.\d+', value), 'runtime version required')
    return tuple(map(int, value.split('.'))) >= minimum


def resolve(policy, adapter, task, *, tier=None, authority_ref=None, observations=None, profile=None):
    validate(policy)
    require(adapter in policy['adapters'] and task in policy['tasks'], 'unknown adapter or task')
    selected_tier = tier or policy['tasks'][task]
    require(selected_tier in TIERS, 'unknown tier')
    if selected_tier == 'premium':
        require(type(authority_ref) is str and authority_ref.strip(), 'separate premium authorization required')
    choice = deepcopy(policy['adapters'][adapter][selected_tier])
    # Profile is an explicit parsed configuration observation, not an arbitrary file lookup.
    if profile is not None:
        require(type(profile) is dict and set(profile) <= {'model', 'effort'}, 'profile observation fields')
        if adapter == 'codex':
            require(all(profile.get(k, choice[k]) == choice[k] for k in ('model', 'effort')),
                    'Codex profile overrides task selection; reconcile the project-owned profile')
    result = {'outcome': 'configured', 'changed': False, 'adapter': adapter, 'task': task,
              'tier': selected_tier, **choice, 'authority_ref': authority_ref,
              'authority_verified': False, 'availability': 'unknown', 'invocation_observed': False,
              'dispatch': {'model': choice['model']}}
    if adapter == 'codex':
        result['dispatch'].update({'model_reasoning_effort': choice['effort'], 'fork_turns': 'none'})
    elif choice['effort'] is not None:
        result['dispatch']['effort'] = choice['effort']
    result['requirements'] = ['Caller verifies authority and actual runtime selection before proceeding.']
    if adapter == 'claude' and choice['effort'] is None:
        result['requirements'].append('No effort override for Haiku; verify model capability, not parent effort.')
    if observations is not None:
        require(type(observations) is dict and set(observations) == {
            'adapter', 'runtime_version', 'models', 'forced_model', 'forced_effort'}, 'observation fields')
        require(observations['adapter'] == adapter, 'observation provider mismatch')
        require(observations['forced_model'] in (None, choice['model']), 'forced model conflicts with task')
        require(observations['forced_effort'] in (None, choice['effort']), 'forced effort conflicts with task')
        if adapter == 'claude':
            require(version_at_least(observations['runtime_version'], (2, 1, 251)), 'Claude invocation model override unsupported')
            if choice['effort'] is not None:
                require(version_at_least(observations['runtime_version'], (2, 1, 292)), 'Claude invocation effort override unsupported')
        require(type(observations['models']) is list, 'model observations required')
        matches = [m for m in observations['models'] if type(m) is dict and m.get('model') == choice['model']]
        require(len(matches) == 1, 'selected model unavailable or ambiguous')
        require(choice['effort'] is None or choice['effort'] in matches[0].get('efforts', []), 'selected effort unavailable')
        result.update(outcome='selected', availability='caller-observed')
    return result


def execute(request):
    require(type(request) is dict, 'request object required')
    operation = request.get('operation')
    if operation in {'registry-inspect', 'registry-plan', 'registry-apply', 'role-compare', 'route-resolve'}:
        from .subagent_registry import execute as registry_execute
        return registry_execute(request)
    common = {'operation', 'engine', 'engine_root'}
    extras = {'defaults': set(), 'inspect': {'project_root'}, 'plan': {'project_root', 'proposed'},
              'apply': {'project_root', 'plan', 'plan_sha256'},
              'compare': {'baseline', 'local', 'candidate'},
              'resolve': {'project_root', 'adapter', 'task', 'tier', 'authority_ref', 'observations', 'profile'}}
    require(operation in extras and set(request) <= common | extras[operation], 'operation or request fields')
    if operation == 'defaults':
        return {'outcome': 'proposed', 'changed': False, 'policy': defaults(), 'native_settings_proposal': native_defaults(defaults())}
    if operation == 'inspect':
        return inspect(request['project_root'])
    if operation == 'plan':
        return plan(request['project_root'], request['proposed'])
    if operation == 'apply':
        return apply(request['project_root'], request['plan'], request['plan_sha256'])
    if operation == 'compare':
        return compare(request['baseline'], request['local'], request['candidate'])
    current = inspect(request['project_root'])
    require(current['policy'] is not None, 'policy missing; explicitly initialize before delegation')
    return resolve(current['policy'], request['adapter'], request['task'],
                   **{k: request[k] for k in ('tier', 'authority_ref', 'observations', 'profile') if k in request})
