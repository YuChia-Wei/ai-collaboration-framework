"""Real SDK/Roslyn acceptance for RefactorTool; run against a built or published tool."""
import argparse
import base64
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import unittest


class RefactoringAcceptance(unittest.TestCase):
    def setUp(self):
        self.area = tempfile.TemporaryDirectory(prefix="rename-", dir=ARGS.work)
        self.addCleanup(self.area.cleanup)
        self.root = pathlib.Path(self.area.name).resolve()
        self.a = self.root / "A"
        self.b = self.root / "B"
        self.a.mkdir()
        self.b.mkdir()
        (self.root / "global.json").write_text(json.dumps({"sdk": {"version": ARGS.sdk_version, "rollForward": "disable"}}), encoding="utf-8")
        self.project = self.a / "A.csproj"
        self.project.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><GenerateDocumentationFile>true</GenerateDocumentationFile></PropertyGroup></Project>', encoding="utf-8")
        (self.b / "B.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework><GenerateDocumentationFile>true</GenerateDocumentationFile></PropertyGroup><ItemGroup><ProjectReference Include="../A/A.csproj" /></ItemGroup></Project>', encoding="utf-8")
        self.solution = self.root / "Demo.slnx"
        self.solution.write_text('<Solution><Project Path="A/A.csproj" /><Project Path="B/B.csproj" /></Solution>', encoding="utf-8")
        self.source = self.a / "Service.cs"
        self.source.write_bytes(b'namespace Demo;\r\npublic interface IService { int Get(int value); }\r\npublic class Service : IService {\r\n    public int Field = 1;\r\n    public int Property { get; set; }\r\n    public virtual int Get(int value) { int local = value; return local + Field; }\r\n    public int Get(string value) => value.Length;\r\n}\r\npublic class Derived : Service { public override int Get(int value) => base.Get(value); }\r\npublic class Other { public int Get(int value) => value; }\r\n')
        self.consumer = self.b / "Use.cs"
        self.consumer.write_text('using Demo;\n/// <see cref="Service.Get(int)"/>\npublic class Use { public int Run() { IService service = new Service(); return service.Get(2) + new Derived().Get(3) + new Other().Get(4); } public string Name => nameof(IService.Get); public string Text => "Get Service"; } // Get Service\n', encoding="utf-8")
        self.restore()
        self.sequence = 0

    def run_dotnet(self, *args):
        run = subprocess.run(["dotnet", *map(str, args)], cwd=self.root, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return run.stdout

    def restore(self):
        self.run_dotnet("restore", self.solution, "--source", self.root, "-p:NuGetAudit=false")

    def invoke(self, command, **kwargs):
        arguments = [str(ARGS.tool)]
        if ARGS.tool.suffix == ".dll":
            arguments.insert(0, "dotnet")
        for key, value in kwargs.items():
            arguments.extend(["--" + key, str(value)])
        arguments.insert(2 if ARGS.tool.suffix == ".dll" else 1, command)
        run = subprocess.run(arguments, cwd=getattr(self, "call_directory", self.root), capture_output=True, text=True, encoding="utf-8", timeout=180)
        self.assertEqual(run.stderr, "", run.stderr)
        try:
            result = json.loads(run.stdout)
        except json.JSONDecodeError:
            self.fail(run.stdout)
        return run.returncode, result

    def preview(self, *, plan_path=None, **overrides):
        self.sequence += 1
        request = dict(workspace=str(self.solution), project=str(self.project), symbol="M:Demo.Service.Get(System.Int32)", newName="Fetch")
        request.update(overrides)
        request = {k: v for k, v in request.items() if v is not None}
        path = self.root / f"request{self.sequence}.json"
        path.write_text(json.dumps(request), encoding="utf-8")
        self.plan_path = plan_path or self.root / f"plan{self.sequence}.json"
        return self.invoke("preview", request=path, plan=self.plan_path)

    def snapshot(self):
        return {str(p): p.read_bytes() for p in self.root.rglob("*.cs") if "obj" not in p.parts and "bin" not in p.parts}

    def test_cross_project_related_members_cref_nameof_preview_apply(self):
        original = self.snapshot()
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.snapshot(), original)
        plan = json.loads(self.plan_path.read_text(encoding="utf-8"))
        self.assertEqual(len(plan["projects"]), 2)
        self.assertTrue(plan["patch"])
        self.assertEqual(plan["projects"][0]["nullable"], "Enable")
        self.assertTrue(plan["relatedSymbols"])
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertTrue(all(f["state"] == "applied" for f in result["files"]))
        source = self.source.read_text(encoding="utf-8")
        consumer = self.consumer.read_text(encoding="utf-8")
        self.assertIn("interface IService { int Fetch(int value); }", source)
        self.assertIn("override int Fetch(int value) => base.Fetch(value)", source)
        self.assertIn("public int Get(string value)", source)
        self.assertIn("class Other { public int Get(int value)", source)
        self.assertIn("service.Fetch(2)", consumer)
        self.assertIn("new Other().Get(4)", consumer)
        self.assertIn('cref="Service.Fetch(int)"', consumer)
        self.assertIn("nameof(IService.Fetch)", consumer)
        self.assertIn('"Get Service"', consumer)
        self.assertIn("// Get Service", consumer)
        self.assertEqual(self.source.read_bytes().count(b"\n"), self.source.read_bytes().count(b"\r\n"))
        self.assertTrue(self.source.exists())
        self.run_dotnet("build", self.solution, "--no-restore", "--nologo")

    def test_overload_group(self):
        self.consumer.write_text(self.consumer.read_text().replace("nameof(IService.Get)", "nameof(Service.Get)"))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "ambiguous_nameof")
        code, result = self.preview(renameOverloads=True)
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertIn("int Fetch(string value)", self.source.read_text())
        self.assertIn("nameof(Service.Fetch)", self.consumer.read_text())

    def test_type_and_interface(self):
        for symbol, name in [("T:Demo.Service", "RenamedService"), ("T:Demo.IService", "IRenamedService")]:
            with self.subTest(symbol=symbol):
                code, result = self.preview(symbol=symbol, newName=name)
                self.assertEqual(code, 0, result)
                code, result = self.invoke("apply", plan=self.plan_path)
                self.assertEqual(code, 0, result)
                self.assertIn(name, self.consumer.read_text())

    def test_property_field_parameter_local(self):
        for symbol, name in [("P:Demo.Service.Property", "Value"), ("F:Demo.Service.Field", "Data")]:
            code, result = self.preview(symbol=symbol, newName=name)
            self.assertEqual(code, 0, result)
            code, result = self.invoke("apply", plan=self.plan_path)
            self.assertEqual(code, 0, result)
        for token, new_name in [("value", "argument"), ("local", "answer")]:
            line = self.source.read_text().splitlines()[5]
            column = line.index(token) + 1
            code, result = self.preview(project=None, symbol=None, file=str(self.source), line=6, column=column, newName=new_name)
            self.assertEqual(code, 0, result)
            code, result = self.invoke("apply", plan=self.plan_path)
            self.assertEqual(code, 0, result)
        self.assertIn("return answer + Data", self.source.read_text())

    def test_invalid_and_ambiguous_selection(self):
        original = self.snapshot()
        for options in [dict(symbol="M:Demo.Service.Get"), dict(newName="class"), dict(newName="bad-name"), dict(project=None, symbol=None, file=str(self.source), line=6, column=1)]:
            code, result = self.preview(**options)
            self.assertEqual(code, 2, result)
            if "newName" in options:
                self.assertEqual(result["code"], "invalid_name")
            self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_collision_rejected(self):
        code, result = self.preview(newName="Property")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "name_collision")

    def test_drift_in_unmodified_source(self):
        code, result = self.preview(symbol="F:Demo.Service.Field", newName="Data")
        self.assertEqual(code, 0, result)
        self.consumer.write_text(self.consumer.read_text() + "// user edit\n")
        original = self.snapshot()
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "input_drift")
        self.assertEqual(self.snapshot(), original)

    def test_new_source_file_drift(self):
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        (self.a / "Added.cs").write_text("class Added {}\n")
        original = self.snapshot()
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "plan_drift")
        self.assertEqual(self.snapshot(), original)

    def test_tampered_plan(self):
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        plan["edits"][0]["after"] = base64.b64encode(b"bad").decode()
        self.plan_path.write_text(json.dumps(plan))
        original = self.snapshot()
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "plan_drift")
        self.assertEqual(self.snapshot(), original)

    def test_multiple_frameworks(self):
        self.project.write_text(self.project.read_text().replace("<TargetFramework>net10.0</TargetFramework>", "<TargetFrameworks>net10.0;net9.0</TargetFrameworks>"))
        code, result = self.preview(framework="net10.0")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "multiple_frameworks")

    def test_linked_file(self):
        external = self.root / "Linked.cs"
        external.write_text("class Linked {}")
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup><Compile Include="../Linked.cs" Link="Linked.cs" /></ItemGroup></Project>'))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "linked_file")

    def test_missing_reference(self):
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup><ProjectReference Include="Missing.csproj" /></ItemGroup></Project>'))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertFalse(self.plan_path.exists())

    def test_generated_relation(self):
        generated = self.a / "Generated.g.cs"
        generated.write_text("namespace Demo; class Generated : Service { public override int Get(int value) => base.Get(value); }")
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertIn(result["code"], ["uneditable_symbol", "uneditable_reference", "uneditable_source"])

    def test_external_override(self):
        self.source.write_text(self.source.read_text().replace("public int Field = 1;", 'public override string ToString() => "Service"; public int Field = 1;'))
        code, result = self.preview(symbol="M:Demo.Service.ToString", newName="Describe")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "uneditable_symbol")

    def test_baseline_errors_remain_visible(self):
        (self.b / "Broken.cs").write_text("class Broken { MissingType field; }")
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["baselineErrors"])
        self.assertEqual(result["newErrors"], [])

    def test_conditional_configuration_is_explicit(self):
        (self.a / "Conditional.cs").write_text("#if DEBUG\nclass Active {}\n#else\nclass Inactive {}\n#endif\n")
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertIn("DEBUG", plan["projects"][0]["defines"])
        self.assertTrue(any("Inactive conditional" in line for line in plan["limits"]))

    def test_existing_error_does_not_mask_new_local_collision(self):
        (self.b / "Broken.cs").write_text("class Broken { MissingType field; }")
        line = self.source.read_text().splitlines()[5]
        original = self.snapshot()
        code, result = self.preview(project=None, symbol=None, file=str(self.source), line=6, column=line.index("local") + 1, newName="value")
        self.assertEqual(code, 2, result)
        self.assertIn(result["code"], ["rename_conflict", "new_compilation_errors"])
        self.assertEqual(self.snapshot(), original)

    def test_baseline_error_after_renamed_token_is_mapped(self):
        self.source.write_text(self.source.read_text().replace("public int Field = 1;", "public int Field = 1; MissingType broken;"))
        code, result = self.preview(symbol="F:Demo.Service.Field", newName="LongerFieldName")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["baselineErrors"])

    def test_source_generator_output(self):
        (self.a / "Json.cs").write_text("using System.Text.Json.Serialization; [JsonSerializable(typeof(string))] internal partial class Context : JsonSerializerContext {}")
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "source_generators")

    def test_non_csharp_solution_member(self):
        vb = self.root / "VisualBasic.vbproj"
        vb.write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net10.0</TargetFramework></PropertyGroup></Project>')
        self.solution.write_text(self.solution.read_text().replace("</Solution>", '<Project Path="VisualBasic.vbproj" /></Solution>'))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unsupported_project")

    def test_read_only_reference_rejected_before_write(self):
        import stat
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        original = self.snapshot()
        try:
            self.consumer.chmod(stat.S_IREAD)
            code, result = self.invoke("apply", plan=self.plan_path)
            self.assertEqual(code, 2, result)
            self.assertEqual(self.snapshot(), original)
            self.assertFalse(result["sourceWrites"])
        finally:
            self.consumer.chmod(stat.S_IREAD | stat.S_IWRITE)

    def test_imported_framework_and_configuration(self):
        props = self.root / "Directory.Build.props"
        props.write_text('<Project><PropertyGroup><TargetFramework>net10.0</TargetFramework><DefineConstants>$(DefineConstants);CUSTOM</DefineConstants></PropertyGroup></Project>')
        self.project.write_text(self.project.read_text().replace("<TargetFramework>net10.0</TargetFramework>", ""))
        code, result = self.preview(configuration="Release")
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertEqual(plan["projects"][0]["framework"], "net10.0")
        self.assertEqual(plan["projects"][0]["configuration"], "Release")
        self.assertIn("CUSTOM", plan["projects"][0]["defines"])
        self.assertNotIn("DEBUG", plan["projects"][0]["defines"])

    def test_classic_solution_with_dotted_folder(self):
        sln = self.root / "Classic.sln"
        sln.write_text('Microsoft Visual Studio Solution File, Format Version 12.00\n'
                       'Project("{2150E333-8FDC-42A3-9474-1A3956D46DE8}") = "src.Core", "src.Core", "{F0000000-0000-0000-0000-000000000000}"\nEndProject\n'
                       'Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "A", "A\\A.csproj", "{A0000000-0000-0000-0000-000000000000}"\nEndProject\n'
                       'Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "B", "B\\B.csproj", "{B0000000-0000-0000-0000-000000000000}"\nEndProject\nGlobal\nEndGlobal\n')
        code, result = self.preview(workspace=str(sln))
        self.assertEqual(code, 0, result)

    def test_patch_preserves_no_final_newline_and_bom(self):
        self.source.write_bytes(b'\xef\xbb\xbf' + self.source.read_bytes().rstrip(b'\r\n'))
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertIn("\\ No newline at end of file", plan["patch"])
        edit = next(e for e in plan["edits"] if pathlib.Path(e["path"]) == self.source)
        after = base64.b64decode(edit["after"])
        self.assertTrue(after.startswith(b'\xef\xbb\xbf'))
        self.assertFalse(after.endswith(b'\n'))

    def test_ambiguous_position_never_selects_first_overload(self):
        self.consumer.write_text(self.consumer.read_text().replace("nameof(IService.Get)", "nameof(Service.Get)"))
        line = self.consumer.read_text().splitlines()[2]
        column = line.index("nameof(Service.Get)") + len("nameof(Service.") + 1
        code, result = self.preview(project=None, symbol=None, file=str(self.consumer), line=3, column=column, renameOverloads=True)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "ambiguous_symbol")

    def test_inherited_name_collision(self):
        code, result = self.preview(newName="ToString")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "name_collision")

    def test_configuration_cannot_inject_msbuild_properties(self):
        code, result = self.preview(configuration="Debug,DefineConstants=OTHER")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "invalid_configuration")

    def test_workspace_sdk_independent_of_calling_directory(self):
        self.call_directory = self.root / "caller"
        self.call_directory.mkdir()
        (self.call_directory / "global.json").write_text('{"sdk":{"version":"99.0.100","rollForward":"disable"}}')
        code, result = self.preview()
        self.assertEqual(code, 0, result)

    def test_project_entry_keeps_project_references(self):
        code, result = self.preview(workspace=str(self.b / "B.csproj"))
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertEqual(len(plan["projects"]), 2)

    def test_preview_artifact_cannot_enter_source_or_configuration(self):
        original = self.snapshot()
        for path in [self.a / "Injected.cs", self.a / "plan.json", self.root / "global.json"]:
            code, result = self.preview(plan_path=path)
            self.assertEqual(code, 2, result)
            self.assertEqual(result["code"], "unsafe_plan_path")
            if path.name != "global.json":
                self.assertFalse(path.exists())
        self.assertEqual(self.snapshot(), original)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", type=pathlib.Path, required=True)
    parser.add_argument("--work", type=pathlib.Path, required=True)
    parser.add_argument("--sdk-version", default="10.0.403")
    ARGS, remaining = parser.parse_known_args()
    ARGS.tool = ARGS.tool.resolve()
    ARGS.work.mkdir(parents=True, exist_ok=True)
    unittest.main(argv=[__file__, *remaining])
