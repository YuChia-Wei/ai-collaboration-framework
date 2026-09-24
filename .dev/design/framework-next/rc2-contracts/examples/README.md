# Illustrative format documents

These files are **documentation models**, not inputs supported by the existing
parser and not records of actual assembly, engine execution, installation,
publication or target adoption. S1 does not run a product/schema validator.

- `source-installation.example.json` lists all 18 delivered skill IDs with no
  knowledge and both adapters. Its zero catalog hashes are deliberately unresolved.
- `mq-lab-installation.example.json` includes the common/.NET packages and preserves
  the fixed target's 20 selectors as 40 package-specific normative bindings. Its
  authority hashes are observed fixed-target bytes; its catalog pin remains zero.
- `content-package.example.yaml`, `selection.example.json`, `catalog.example.json`,
  `catalog-files.example.json`, `subset.example.json`, `files.example.json`,
  `lock.example.json`, and the two `*-build.example.json` files demonstrate the
  closed shapes and parent/subset digest calculation with a tiny fictional package.
- `model-input-bytes.json` makes that tiny model's UTF-8 content explicit. The zero
  source commit, zero installation identity and invented engine/generator bytes are
  fictional. The package is not part of the S2 member assignment. Calculated hashes
  describe the model only, not an actual source commit or admissible engine pin.

Example completion timestamps/runtime strings in build-shaped documents are sample
fields, not execution observations. Only JSON/YAML/UTF-8 readability and local links
are applicable S1 evidence. A future fixture must use its own actual execution
record. A real target or runtime result must remain separately identified.

Normative shapes are in [the schema bundle](../schemas/contracts.schema.json);
cross-document, lexical, safety and digest requirements are in
[formats.md](../formats.md). Do not treat JSON Schema alone as a full validator.
