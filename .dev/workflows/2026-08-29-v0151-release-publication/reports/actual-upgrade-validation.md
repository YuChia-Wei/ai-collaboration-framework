# v0.15.1 Actual Package Admission

## Subject

- Package source commit: `57c7250b4fdc56fd258ea9dc2539c261ad431be1`.
- Package ID: `ai-collaboration-framework-v0.15.1`.
- Candidate ZIP SHA-256: `7b65a15c13c6788ae0a6f2b18971bc0650568466afc21a576a846c5e0bda52a3`.
- v0.15.0 source ZIP SHA-256: `d3d6e27154df567fef025990ef4c367a1cc98ec1316980a76eed6e2d1005fe11`.
- Command owner: `.github/scripts/validate-v0151-actual-upgrade.py`.

## Attempts

The first local attempt executed but failed during clean-install apply because
the sandbox denied a transaction-directory write inside the isolated target
repository's `.git` directory. Its terminal outcome remains `failed` with
failure reason `clean-install-exit-1`; it is not reused as passing evidence.

The second attempt used the same package inputs and command after the
permission boundary materially changed. It completed in 258.444528 seconds
with terminal outcome `passed` and proved:

- actual clean-install package apply executed;
- actual v0.15.0-to-v0.15.1 package apply executed;
- the package, files manifest, migration manifest, payload fingerprint, and
  fixed-head auditor binding matched the declared candidate;
- clean-install and upgrade receipts were produced and read back; and
- every Git inspection phase reported `outcome: passed`.

The privacy-safe raw terminals are intentionally ignored local evidence under
`.dev/ai-context/local/validation/v0151-actual-upgrade-57c7250b*/`. The first
failure and later pass remain separate records.

## Evidence Boundary

This is actual local package execution against the exact package-source
commit. It is not hosted PR evidence and does not authorize merge, tag, or
publication. The PR candidate workflow must rebuild the final PR head and
repeat the same actual clean-install and v0.15.0 upgrade gate before merge.
