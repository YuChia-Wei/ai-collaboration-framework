# Observed Generated Test Output

These are byte-identical retained copies of the first model-generated candidate
from the ignored `generation/project` output. The filename is shortened only
for this evidence archive. The original generated files were compiled and run
in two projects copied from the canonical bdd-step-methods fixture, without
copying its original BudgetQueryTests.cs. The source, configuration and package
selection were unchanged. These copies are evidence, not active test projects.

`mapping-at-generation.md` is the unmodified stage output: its unexecuted status
was true when generation completed. The subsequent actual build/test outcomes
and independent semantic review are in ../../observed-results.json and
../../remediation-report.md. Do not rewrite the original stage's chronology.

To reproduce, create separate temporary project copies from the canonical
fixture's BudgetQuery.cs, Directory.Build.props, NuGet.Config and the two csproj
files. Add each corresponding retained file as GeneratedBudgetQueryTests.cs,
then use the same build and test commands recorded in observed-results.json.
Do not include the original example test file in those generated-only projects.
