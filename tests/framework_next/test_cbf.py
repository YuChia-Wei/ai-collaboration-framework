"""T7 uses the CBF public file request and its distinct result/exit contract."""
from __future__ import annotations

import copy
import uuid

from test_knowledge import PublicCase, digest


class CbfTests(PublicCase):
    def test_selected(self):
        self.prepare('problem-frame-author', 'problem_frame.py', ['C4-config', 'C6-binding', 'T7-round-trip', 'T7-structural-negatives'])
        self.phase('C4-config')
        self.config_checks()
        self.phase('C6-binding')
        self.binding_negative()
        self.require_write_roundtrip()
        self.phase('T7-round-trip')
        record = {'family': 'problem-frame.cbf', 'schema_version': '1.0.0', 'id': 'cbf-' + uuid.uuid4().hex,
                  'frame_key': 'selected-fixture', 'title': 'Synthetic bounded CBF', 'derived_from': None,
                  'sources': [{'id': 'SRC1', 'kind': 'requirement', 'reference': 'synthetic:intent', 'revision': None,
                               'locator': 'Fictional input only', 'sha256': None, 'authority': 'proposed', 'authority_reference': None}],
                  'statements': [{'id': name, 'category': category, 'text': text, 'basis': 'stated', 'source_ids': ['SRC1']}
                                 for name, category, text in [('ACTOR1', 'actor', 'A caller.'), ('CMD1', 'command', 'Request a value.'),
                                                              ('DOMAIN1', 'controlled-domain', 'Local fixture state.')]],
                  'scenarios': [{'id': 'SC1', 'title': 'Observe one result', 'source_ids': ['SRC1'], 'given': ['A fixture'],
                                 'when': ['The caller requests a value'], 'then': [{'id': 'THEN1', 'text': 'The exact value is unresolved.',
                                 'basis': 'unresolved', 'source_ids': [], 'statement_ids': ['CMD1']}], 'tests_anchor': []}],
                  'open_questions': [{'id': 'Q1', 'text': 'Which value is required?', 'related_ids': ['THEN1']}]}
        reference = record['id'] + '.cbf.json'
        created = self.invoke('create', reference=reference, record=record)
        path = self.store / reference
        raw = path.read_bytes()
        self.assertEqual(created['subject_sha256'], digest(raw))
        expected_inventory = [{'id': row['id'], 'kind': 'statement', 'pointer': '/statements/' + str(index), 'scenario_id': None}
                              for index, row in enumerate(record['statements'])] + [
            {'id': 'SC1', 'kind': 'scenario', 'pointer': '/scenarios/0', 'scenario_id': 'SC1'},
            {'id': 'THEN1', 'kind': 'assertion', 'pointer': '/scenarios/0/then/0', 'scenario_id': 'SC1'}]
        expected = {'contract': 'problem-frame.cbf.structural-result@1.0.0', 'status': 'valid', 'family': 'problem-frame.cbf',
                    'schema_version': '1.0.0', 'id': record['id'], 'subject_sha256': digest(raw),
                    'criterion_inventory': expected_inventory, 'counts': {'statement': 3, 'scenario': 1, 'assertion': 1},
                    'unresolved_ids': ['THEN1'], 'source_ids': ['SRC1'], 'question_ids': ['Q1']}
        self.assertEqual(created['result']['structure'], expected)
        for operation in ('inspect', 'validate', 'render'):
            result = self.invoke(operation, reference=reference, expected_sha256=created['subject_sha256'])
            self.assertEqual(result['subject_sha256'], digest(raw))
            self.assertEqual(result['result']['structure'], expected)
            self.assertEqual(path.read_bytes(), raw)
        self.phase('T7-structural-negatives')
        self.invoke('create', reference=reference, record=record, expect='conflict')
        self.invoke('inspect', reference=reference, expected_sha256=digest(b'stale fixture'), expect='conflict')
        # One second destination, never published, for structural refusal before writes.
        alternate = copy.deepcopy(record)
        alternate['id'] = 'cbf-' + uuid.uuid4().hex
        alternate_ref = alternate['id'] + '.cbf.json'
        for field, value, outcome in [('family', 'unknown', 'unsupported-family'), ('schema_version', '99.0.0', 'unsupported-version')]:
            invalid = {**alternate, field: value}
            self.invoke('create', reference=alternate_ref, record=invalid, expect=outcome)
        duplicate = copy.deepcopy(alternate)
        duplicate['statements'][1]['id'] = duplicate['statements'][0]['id']
        self.invoke('create', reference=alternate_ref, record=duplicate, expect='invalid-input')
        missing = copy.deepcopy(alternate)
        missing['scenarios'][0]['then'][0]['statement_ids'] = ['MISSING']
        self.invoke('create', reference=alternate_ref, record=missing, expect='invalid-input')
        missing = copy.deepcopy(alternate)
        missing['open_questions'] = []
        self.invoke('create', reference=alternate_ref, record=missing, expect='invalid-input')
        self.invoke('create', reference=alternate_ref, record=record, expect='invalid-input')
        legacy = self.store / 'legacy.yaml'
        self.run.write(legacy, b'family: legacy\n')
        result = self.invoke('inspect', reference=legacy.name, expect='unsupported-format')
        self.assertEqual(result['subject_sha256'], digest(legacy.read_bytes()))
        self.assertEqual(path.read_bytes(), raw)
        self.assertFalse((self.store / alternate_ref).exists())
        self.finish()
