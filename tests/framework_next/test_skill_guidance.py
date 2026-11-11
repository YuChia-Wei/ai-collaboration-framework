"""Selected knowledge contributes managed references; skill entries stay unchanged."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / 'src')]
from distribution import catalog
from distribution.content import descriptor, load_content_package, skill_guidance_text
from distribution.data import json_bytes
from distribution.package import load_package
from test_distribution_contracts import knowledge, skill
from test_skill_naming import source_blob, tiny_catalog


def guidance_catalog(*, consume=True, operations=('review',), duplicate=False):
    parent = tiny_catalog()
    consumer = skill()
    consumer['knowledge_consumption'] = []
    payload = {}
    for pid in ('common', 'other'):
        doc = knowledge()
        doc['id'] = pid
        doc['members'].append({'path': 'guidance.md', 'kind': 'skill-guidance'})
        doc['resources'].insert(0, {'id': 'guidance', 'path': 'guidance.md',
            'kind': 'skill-guidance', 'rule_ids': [], 'capabilities': ['review'],
            'operations': list(operations), 'technology_profile': None})
        payload[('knowledge', pid, 'content-package.yaml')] = json_bytes(doc)
        payload[('knowledge', pid, 'README.md')] = b'# Ordinary knowledge\n'
        payload[('knowledge', pid, 'guidance.md')] = f'Use {pid.upper()} guidance for this operation.\n'.encode()
        consumer['knowledge_consumption'].append({'id': pid, 'package': pid, 'version': '0.1.0',
            'operations': ['review'], 'resources': ['guidance', 'index'] if consume else ['index'],
            'requirement': 'optional', 'on_missing': 'unavailable'})
    if duplicate:
        row = deepcopy(consumer['knowledge_consumption'][0])
        row['id'] = 'common-again'
        consumer['knowledge_consumption'].insert(1, row)
    payload[('skill', 'reviewer', 'skill-package.yaml')] = json_bytes(consumer)
    return replace_payload(parent, payload)


def replace_payload(parent, payload):
    """Rebuild fictional source identities after authoring fixture package bytes."""
    doc, inventory, contents = deepcopy(parent.document), deepcopy(parent.inventory), dict(parent.contents)
    sources = {r['path']: r for r in doc['build_inputs']}
    rows = {(r['kind'], r['owner'], r['member']): r for r in inventory['files']}
    packages = dict(parent.packages)
    for (kind, pid, member), raw in payload.items():
        directory = 'skills' if kind == 'skill' else 'knowledge'
        source = source_blob(f'src/{directory}/{pid}/{member}', raw)
        sources[source.path] = source.identity()
        name = f'packages/{kind}/{pid}/{member}'
        rows[(kind, pid, member)] = {'path': name, 'kind': kind, 'owner': pid,
                                    'member': member, 'source': source.identity()}
        contents[name] = raw
        if member in ('skill-package.yaml', 'content-package.yaml'):
            packages[(kind, pid)] = (load_package if kind == 'skill' else load_content_package)(source)
    doc['components'] = sorted((descriptor(kind, package) for (kind, _), package in packages.items()),
                               key=lambda row: (row['kind'], row['id']))
    doc['build_inputs'] = [sources[name] for name in sorted(sources)]
    inventory['files'] = sorted(rows.values(), key=lambda row: row['path'])
    raw = {catalog.PARENT_METADATA[0]: json_bytes(doc), catalog.PARENT_METADATA[1]: json_bytes(inventory)}
    doc, inventory, pin = catalog.parent_documents(raw)
    packages = catalog.packages_from(doc, inventory, contents)
    return catalog.Catalog(None, doc, inventory, pin, raw, contents, packages)


def project(parent, knowledge_ids=(), skills=('reviewer',)):
    desired = {'selection_version': 2, 'catalog': parent.pin, 'skills': list(skills),
               'knowledge': list(knowledge_ids), 'adapters': ['claude', 'codex'],
               'bindings': [], 'skill_naming': 'original'}
    selected = catalog.resolve_selection(parent, desired)
    selected['catalog'] = parent.pin
    keys = {(c['kind'], c['id']) for c in selected['components']}
    payload, templates = {}, {}
    for row in parent.inventory['files']:
        if (row['kind'], row['owner']) in keys:
            directory = 'skills' if row['kind'] == 'skill' else 'knowledge'
            payload[f".ai/core/{directory}/{row['owner']}/{row['member']}"] = parent.contents[row['path']]
        elif row['kind'] == 'adapter':
            templates[row['owner']] = parent.contents[row['path']]
    rows, output = catalog.project_members(parent.document, parent.inventory, selected, payload, templates)
    return selected, rows, output


class SkillGuidanceTests(unittest.TestCase):
    def test_selected_unselected_other_and_deselected_references_preserve_entries(self):
        parent = guidance_catalog()
        empty = project(parent)
        for selected, included, excluded in ((('common',), 'COMMON', 'OTHER'),
                                              (('other',), 'OTHER', 'COMMON')):
            _, rows, output = project(parent, selected)
            reference = f'.ai/core/skills/reviewer/references/knowledge/{selected[0]}/guidance.md'
            self.assertEqual(output[reference], f'Use {included} guidance for this operation.\n'.encode())
            self.assertNotIn(reference, empty[2])
            self.assertNotIn(f'.ai/core/skills/reviewer/references/knowledge/{excluded.lower()}/guidance.md', output)
            for runtime in ('agents', 'claude'):
                target = f'.{runtime}/skills/reviewer/SKILL.md'
                self.assertEqual(output[target], empty[2][target])
            self.assertEqual(output['.ai/core/skills/reviewer/SKILL.md'], empty[2]['.ai/core/skills/reviewer/SKILL.md'])
            catalog.subset_inventory(parent.document, parent.inventory, project(parent, selected)[0], rows)
            for row in rows['files']:
                self.assertEqual(row['sha256'], catalog.digest(output[row['destination']]))
                if row['kind'] == 'payload':
                    kind, pid = row['owner'].split('/')
                    member = row['destination'].split('/', 4)[4]
                    self.assertEqual(output[row['destination']], parent.contents[f'packages/{kind}/{pid}/{member}'])
        self.assertEqual(project(parent), empty)  # Deselecting reproduces the original entries.

    def test_consumption_and_operation_are_required_and_duplicates_emit_once(self):
        for parent in (guidance_catalog(consume=False), guidance_catalog(operations=('implement',))):
            output = project(parent, ('common',))[2]
            self.assertFalse(any('/references/knowledge/' in name for name in output))
        parent = guidance_catalog(duplicate=True)
        first = project(parent, ('common',))
        self.assertEqual(first, project(parent, ('common',)))
        self.assertEqual(sum('/references/knowledge/' in name for name in first[2]), 1)

    def test_source_and_generated_guidance_tampering_are_rejected(self):
        parent = guidance_catalog()
        selected, rows, output = project(parent, ('common',))
        catalog.verify_subset_contents(parent.document, parent.inventory, selected, rows, output)
        for name in ('.ai/core/knowledge/common/guidance.md',
                     '.ai/core/skills/reviewer/references/knowledge/common/guidance.md'):
            altered = dict(output)
            altered[name] += b'Injected text.\n'
            with self.subTest(name=name), self.assertRaises(ValueError):
                catalog.verify_subset_contents(parent.document, parent.inventory, selected, rows, altered)

    def test_guidance_is_bounded_portable_prose_and_cannot_allocate_rules(self):
        for raw in (b'', b' ' * 8193, b'---\nname: override', b'\xef\xbb\xbf---\nname: override',
                    b'[link](other.md)',
                    b'[link][ref]', b'[ref]: other.md', b'<a href="other.md">',
                    b'[choose [this]](other.md)', b'[multi\nline](other.md)',
                    b'![image [label]](other.png)', b'<https://example.test>',
                    b'Use C:\\private\\file', b'Read src/private.md', b'null\x00'):
            with self.subTest(raw=raw[:40]), self.assertRaises(ValueError):
                skill_guidance_text(raw)
        self.assertEqual(skill_guidance_text(b'Example text: https://example.test'),
                         'Example text: https://example.test')
        doc = knowledge()
        doc['resources'][0].update(kind='skill-guidance')
        with self.assertRaisesRegex(ValueError, 'requires a matching Markdown member'):
            load_content_package(source_blob('content-package.yaml', json_bytes(doc)))
        for field, value in (('rule_ids', ['RULE-001']), ('technology_profile', 'dotnet-backend')):
            altered = deepcopy(doc)
            member = next(row for row in altered['members'] if row['path'] == altered['resources'][0]['path'])
            member['kind'] = 'skill-guidance'
            altered['resources'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                load_content_package(source_blob('content-package.yaml', json_bytes(altered)))

    def test_real_implementation_skills_have_dotnet_text_only_when_selected(self):
        from test_contracts import source_inventory
        _, _, contents = source_inventory()
        owners = ('slice-implementer', 'local-change-implementer')
        selected = {('skill', name) for name in owners} | {('knowledge', name) for name in ('dotnet', 'engineering-common')}
        payload = {key: raw for key, raw in contents.items() if key[:2] in selected}
        parent = replace_payload(tiny_catalog(), payload)
        neutral = project(parent, skills=tuple(sorted(owners)))[2]
        specialized = project(parent, ('dotnet', 'engineering-common'), tuple(sorted(owners)))[2]
        fragment = contents[('knowledge', 'dotnet', 'tooling/implementation-guidance.md')]
        for owner in owners:
            for member in ('SKILL.md', 'references/implement.md'):
                self.assertNotIn(b'.NET', neutral[f'.ai/core/skills/{owner}/{member}'])
            for runtime in ('agents', 'claude'):
                target = f'.{runtime}/skills/{owner}/SKILL.md'
                self.assertNotIn(b'.NET', neutral[target])
                self.assertEqual(neutral[target], specialized[target])
            target = f'.ai/core/skills/{owner}/references/knowledge/dotnet/tooling/implementation-guidance.md'
            self.assertNotIn(target, neutral)
            self.assertEqual(specialized[target], fragment)

    def test_reference_inventory_rejects_relocation_unselected_sources_and_missing_consumer(self):
        parent = guidance_catalog()
        selected, rows, output = project(parent, ('common',))
        reference = next(row for row in rows['files'] if '/references/knowledge/' in row['destination'])
        for field, value in (('destination', '.ai/core/skills/reviewer/references/implement.md'),
                             ('owner', 'skill/other/knowledge/common'),
                             ('sha256', '0' * 64)):
            changed = deepcopy(rows)
            next(row for row in changed['files'] if row['destination'] == reference['destination'])[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                catalog.subset_inventory(parent.document, parent.inventory, selected, changed)
        absent, absent_rows, absent_output = project(parent)
        absent_rows['files'].append(reference)
        with self.assertRaises(ValueError):
            catalog.subset_inventory(parent.document, parent.inventory, absent, absent_rows)
        unconsuming = guidance_catalog(consume=False)
        selection, inventory, content = project(unconsuming, ('common',))
        inventory['files'].append(reference)
        inventory['files'].sort(key=lambda row: row['path'])
        content[reference['destination']] = output[reference['destination']]
        # The path/source is safe, but only full projection can admit consumption.
        catalog.subset_inventory(unconsuming.document, unconsuming.inventory, selection, inventory)
        with self.assertRaises(ValueError):
            catalog.verify_subset_contents(unconsuming.document, unconsuming.inventory, selection, inventory, content)


if __name__ == '__main__':
    unittest.main()
