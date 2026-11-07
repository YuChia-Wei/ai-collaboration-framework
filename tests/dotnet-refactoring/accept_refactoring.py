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

    def extract(self, **options):
        request = dict(operation="extract-interface", symbol="T:Demo.Service", newName="ISelected",
                       namespace="Contracts", outputFile=str(self.a / "ISelected.cs"),
                       members=["M:Demo.Service.Get(System.Int32)", "P:Demo.Service.Property"])
        request.update(options)
        return self.preview(**request)

    def test_extract_interface_selected_members_preserve_behavior_and_consumers(self):
        original = self.snapshot()
        project_bytes = self.project.read_bytes()
        code, result = self.extract()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.snapshot(), original)
        plan = json.loads(self.plan_path.read_text())
        self.assertEqual(sorted(e["kind"] for e in plan["edits"]), ["create", "modify"])
        self.assertIn("--- /dev/null", plan["patch"])
        create = next(e for e in plan["edits"] if e["kind"] == "create")
        self.assertEqual(create["before"], "")
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertTrue(all(f["state"] == "applied" for f in result["files"]))
        self.assertEqual(self.project.read_bytes(), project_bytes)
        self.assertEqual(self.consumer.read_bytes(), original[str(self.consumer)])
        self.assertEqual(self.source.read_bytes().replace(b", global::Contracts.ISelected", b""), original[str(self.source)])
        interface = (self.a / "ISelected.cs").read_text()
        self.assertIn("interface ISelected", interface)
        self.assertIn("Property", interface)
        self.assertNotIn("Get(global::System.String", interface)
        self.assertNotIn("Field", interface)
        self.run_dotnet("build", self.solution, "--no-restore", "--nologo")
        # A real consumer uses the extracted contract; independently expected
        # results exercise dispatch, state and preserved concrete overloads.
        b_project = self.b / "B.csproj"
        b_project.write_text(b_project.read_text().replace("<TargetFramework>", "<OutputType>Exe</OutputType><TargetFramework>"))
        (self.b / "Program.cs").write_text('using Demo; using Contracts; ISelected s = new Service(); s.Property=7; System.Console.Write($"{s.Get(2)}|{s.Property}|{new Service().Get(\"abcd\")}");')
        self.assertEqual(self.run_dotnet("run", "--project", b_project, "--no-restore", "-v:q").strip().splitlines()[-1], "3|7|4")

    def test_extract_interface_nullable_generics_ref_out_and_private_setter(self):
        self.source.write_text('''#nullable enable
namespace Demo;
public class Service<T> where T : class {
 public T? Value { get; private set; }
 public T? Read<U>(ref T? value, out int length) where U : unmanaged { length=value?.ToString()?.Length ?? 0; Value=value; return value; }
}
''')
        self.consumer.write_text('public class Use {}')
        original = self.snapshot()
        code, result = self.extract(symbol="T:Demo.Service`1", members=["P:Demo.Service`1.Value", "M:Demo.Service`1.Read``1(`0@,System.Int32@)"])
        self.assertEqual(code, 0, result)
        self.assertEqual(self.snapshot(), original)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        interface = (self.a / "ISelected.cs").read_text()
        for fragment in ["ISelected<T>", "where T : class", "where U : unmanaged", "T?", "ref", "out"]:
            self.assertIn(fragment, interface)
        self.assertNotIn("set;", interface)
        b_project = self.b / "B.csproj"
        b_project.write_text(b_project.read_text().replace("<TargetFramework>", "<OutputType>Exe</OutputType><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors><NoWarn>CS1591</NoWarn><TargetFramework>"))
        (self.b / "Program.cs").write_text('using Demo; using Contracts; ISelected<string> s = new Service<string>(); string? value=null; var first=s.Read<int>(ref value,out var a); value="abc"; var second=s.Read<int>(ref value,out var b); System.Console.Write($"{first is null}|{a}|{second}|{b}|{s.Value}");')
        self.assertEqual(self.run_dotnet("run", "--project", b_project, "--no-restore", "-v:q").strip().splitlines()[-1], "True|0|abc|3|abc")

    def test_extract_interface_refuses_invalid_members_output_and_compile_exclusion(self):
        original = self.snapshot()
        for options in [dict(members=["F:Demo.Service.Field"]), dict(members=["M:Demo.Other.Get(System.Int32)"]),
                        dict(members=["M:Demo.Service.Get"]), dict(members=[]), dict(renameOverloads=True),
                        dict(outputFile=str(self.source)), dict(newName="class"), dict(namespace="bad-name"),
                        dict(outputFile=str(self.root / "Outside.cs")), dict(members=["P:Demo.Service.Property"] * 2)]:
            with self.subTest(options=options):
                code, result = self.extract(**options)
                self.assertEqual(code, 2, result)
                self.assertEqual(result["sourceWrites"], False)
                self.assertFalse(self.plan_path.exists())
                self.assertEqual(self.snapshot(), original)
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Project>'))
        code, result = self.extract()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unsupported_compile_inclusion")
        self.assertEqual(self.snapshot(), original)

    def test_extract_interface_apply_refuses_output_race_source_drift_and_plan_tampering(self):
        original = self.snapshot()
        code, result = self.extract()
        self.assertEqual(code, 0, result)
        path = self.a / "ISelected.cs"
        path.write_bytes(b"// belongs to another writer")
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["sourceWrites"], False)
        self.assertEqual(path.read_bytes(), b"// belongs to another writer")
        path.unlink()
        plan = json.loads(self.plan_path.read_text())
        next(e for e in plan["edits"] if e["kind"] == "create")["after"] = base64.b64encode(b"forged").decode()
        self.plan_path.write_text(json.dumps(plan))
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "plan_drift")
        self.assertEqual(self.snapshot(), original)
        code, result = self.extract()
        self.assertEqual(code, 0, result)
        self.source.write_bytes(self.source.read_bytes() + b"// drift")
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "input_drift")
        self.assertFalse(path.exists())

    def test_extract_interface_refuses_unsupported_shapes_and_visibility_collision(self):
        self.consumer.write_text("public class Use {}")
        for declaration, member in [
            ("public static int Get(int x) => x;", "M:Demo.Service.Get(System.Int32)"),
            ("public int Get(int x = 1) => x;", "M:Demo.Service.Get(System.Int32)"),
            ("[System.Obsolete] public int Get(int x) => x;", "M:Demo.Service.Get(System.Int32)"),
            ("public int this[int x] => x;", "P:Demo.Service.Item(System.Int32)"),
            ("public int Value { get; init; }", "P:Demo.Service.Value")]:
            with self.subTest(declaration=declaration):
                self.source.write_text("namespace Demo; public class Service { " + declaration + " }")
                original = self.snapshot()
                code, result = self.extract(members=[member])
                self.assertEqual(code, 2, result)
                self.assertEqual(result["code"], "unsupported_member")
                self.assertEqual(self.snapshot(), original)
                self.assertFalse(self.plan_path.exists())
        self.source.write_text("namespace Demo; public class Service { public int Get(int x) => x; }")
        code, result = self.extract(newName="Service", namespace="Demo", members=["M:Demo.Service.Get(System.Int32)"])
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "new_compilation_errors")
        self.assertFalse((self.a / "ISelected.cs").exists())

    def test_extract_interface_refuses_file_dependent_inclusion_and_invalid_new_paths(self):
        original = self.snapshot()
        for name in ["payload.cs:stream.cs", "CON.cs", "COM¹.cs", "obj/ISelected.cs"]:
            code, result = self.extract(outputFile=str(self.a / name))
            self.assertEqual(code, 2, result)
            self.assertEqual(result["code"], "invalid_output")
        self.project.write_text(self.project.read_text().replace("</Project>", '<PropertyGroup Condition="Exists(\'ISelected.cs\')"><EnableDefaultCompileItems>false</EnableDefaultCompileItems></PropertyGroup></Project>'))
        code, result = self.extract()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unsupported_compile_inclusion")
        self.assertEqual(self.snapshot(), original)

    def test_extract_interface_refuses_inactive_import_item_expression_and_lowercase_glob(self):
        original = self.snapshot()
        project_text = self.project.read_text()
        (self.a / "ExcludeInterface.targets").write_text('<Project><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Project>')
        (self.a / "Fake.nuget.g.targets").write_text('<Project><Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target></Project>')
        for rule in ['<Import Project="ExcludeInterface.targets" Condition="Exists(\'ISelected.cs\')" />',
                     '<ItemGroup><IgnoredFiles Include="ISelected*.cs"/><Compile Remove="@(IgnoredFiles)" /></ItemGroup>',
                     '<ItemGroup><Compile Remove="ISelected.cs" Condition="\'@(Compile)\' != \'\'" /></ItemGroup>',
                     '<Target Name="RemoveInterface" BeforeTargets="CoreCompile"><ItemGroup><Compile Remove="ISelected.cs" /></ItemGroup></Target>',
                     '<Import Project="Fake.nuget.g.targets" />']:
            with self.subTest(rule=rule):
                self.project.write_text(project_text.replace("</Project>", rule + "</Project>"))
                code, result = self.extract()
                self.assertEqual(code, 2, result)
                self.assertEqual(result["code"], "unsupported_compile_inclusion")
                self.assertEqual(self.snapshot(), original)
        self.project.write_text(project_text)
        (self.a / "Contracts").mkdir()
        b_project = self.b / "B.csproj"
        b_project.write_text(b_project.read_text().replace("</Project>", '<ItemGroup><compile Include="../A/Contracts/**/*.cs" /></ItemGroup></Project>'))
        code, result = self.extract(outputFile=str(self.a / "Contracts/ISelected.cs"))
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unsupported_compile_inclusion")
        self.assertEqual(self.snapshot(), original)

    def test_extract_interface_refuses_existing_type_and_namespace_rebinding(self):
        (self.a / "External.cs").write_text('namespace External { public interface ISelected {} public class Contracts { public class Token {} } }')
        for name, source in [("ISelected", 'namespace Contracts; using External; public class Use { public System.Type Type => typeof(ISelected); }'),
                             ("Token", 'using External; public class Use { public System.Type Type => typeof(Contracts.Token); }')]:
            with self.subTest(name=name):
                self.consumer.write_text(source)
                original = self.snapshot()
                code, result = self.extract(newName=name)
                self.assertEqual(code, 2, result)
                self.assertEqual(result["code"], "name_collision")
                self.assertEqual(self.snapshot(), original)
                self.assertFalse(self.plan_path.exists())

    def test_extract_interface_refuses_future_import_patterns_and_sdk_hooks(self):
        (self.a / "Contracts").mkdir()
        original = self.snapshot()
        project_text = self.project.read_text()
        for rule, destination in [
            ('<Import Project="Contracts/*" />', "Contracts/ISelected.cs"),
            ('<PropertyGroup><ImportSpec>Contracts/*</ImportSpec></PropertyGroup><Import Project="$(ImportSpec)" />', "Contracts/ISelected.cs"),
            ('<PropertyGroup><CustomBeforeMicrosoftCommonTargets>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</CustomBeforeMicrosoftCommonTargets></PropertyGroup>', "Contracts/ISelected.cs"),
            ('<PropertyGroup><DirectoryBuildTargetsPath>$(MSBuildProjectDirectory)/Contracts/ISelected.cs</DirectoryBuildTargetsPath></PropertyGroup>', "Contracts/ISelected.cs"),
            ('<PropertyGroup><_DirectoryBuildTargetsFile>ISelected.cs</_DirectoryBuildTargetsFile></PropertyGroup>', "ISelected.cs")]:
            with self.subTest(rule=rule):
                self.project.write_text(project_text.replace("</Project>", rule + "</Project>"))
                code, result = self.extract(outputFile=str(self.a / destination))
                self.assertEqual(code, 2, result)
                self.assertEqual(result["code"], "unsupported_compile_inclusion", result)
                self.assertEqual(self.snapshot(), original)
                self.assertFalse(self.plan_path.exists())
        (self.a / "Bound.props").write_text('<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>')
        self.project.write_text(project_text.replace("</Project>", '<Import Project="Bound.props" /></Project>'))
        code, result = self.extract()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.snapshot(), original)

    def test_extract_interface_primary_constructor_and_setter_parameter_attribute(self):
        self.consumer.write_text('public class Use {}')
        self.source.write_text('namespace Demo; public class Service { public string Value { get => ""; [param: System.Diagnostics.CodeAnalysis.AllowNull] set {} } }')
        code, result = self.extract(members=["P:Demo.Service.Value"])
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unsupported_member", result)
        source = 'namespace Demo; public class Service(int n) { public int Get(int value) => n + value; }'
        self.source.write_text(source)
        code, result = self.extract(members=["M:Demo.Service.Get(System.Int32)"])
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertEqual(self.source.read_text().replace(" : global::Contracts.ISelected", ""), source)
        b_project = self.b / "B.csproj"
        b_project.write_text(b_project.read_text().replace("<TargetFramework>", "<OutputType>Exe</OutputType><TargetFramework>"))
        (self.b / "Program.cs").write_text('Contracts.ISelected s = new Demo.Service(3); System.Console.Write(s.Get(4));')
        self.assertEqual(self.run_dotnet("run", "--project", b_project, "--no-restore", "-v:q").strip().splitlines()[-1], "7")

    def test_sdk_paths_duplicate_version_uses_selected_sdk_directory(self):
        # SDK paths intentionally allow the same version in a local root and
        # the host root. Use a junction so the test needs no SDK download/copy.
        env = dict(os.environ, DOTNET_CLI_UI_LANGUAGE="en-US")
        info = subprocess.run(["dotnet", "--info"], cwd=self.root, env=env, capture_output=True, text=True, encoding="utf-8", check=True).stdout
        sdk_path = next(line.split(":", 1)[1].strip() for line in info.splitlines() if line.strip().startswith("Base Path:"))
        local_root = self.root / "local-sdk"
        (local_root / "sdk").mkdir(parents=True)
        link = local_root / "sdk" / ARGS.sdk_version
        self.junction(link, pathlib.Path(sdk_path))
        # Remove only the junction itself before TemporaryDirectory cleanup.
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        # A usable dotnet root also needs its runtime and targeting/workload
        # packs. Linking only sdk/ produces a deliberately broken installation.
        host_root = pathlib.Path(sdk_path).parent.parent
        for name in ["shared", "packs", "sdk-manifests"]:
            dependency = local_root / name
            self.junction(dependency, host_root / name)
            self.addCleanup(lambda entry=dependency: entry.rmdir() if entry.exists() else None)
        (self.root / "global.json").write_text(json.dumps({"sdk": {"version": ARGS.sdk_version, "rollForward": "disable", "paths": [str(local_root), "$host$"]}}))
        inventory = self.run_dotnet("--list-sdks")
        self.assertGreaterEqual(sum(line.startswith(ARGS.sdk_version + " ") for line in inventory.splitlines()), 2)
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        code, result = self.extract(members=["M:Demo.Service.Fetch(System.Int32)", "P:Demo.Service.Property"])
        self.assertEqual(code, 0, result)

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

    def test_related_type_overloads_remain_outside_selected_scope(self):
        self.consumer.write_text(self.consumer.read_text().replace("nameof(IService.Get)", "nameof(Service.Get)"))
        original = self.snapshot()
        for symbol in ["M:Demo.IService.Get(System.Int32)", "M:Demo.Derived.Get(System.Int32)"]:
            with self.subTest(symbol=symbol):
                code, result = self.preview(symbol=symbol, renameOverloads=True)
                self.assertEqual(code, 2, result)
                self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "ambiguous_nameof", False))
                self.assertIn("outside the selected rename scope", result["message"])
                self.assertNotIn("review renameOverloads=true", result["message"])
                self.assertFalse(self.plan_path.exists())
                self.assertEqual(self.snapshot(), original)

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

    def test_invalid_requests_are_refused(self):
        request = self.root / "invalid.json"
        original = self.snapshot()
        for content in [None, "{", "null", "{}", '{"workspace":null}', '{"workspace":"a","unknown":true}',
                        '{"workspace":"a","workspace":"b"}', json.dumps({"workspace": str(self.solution)})]:
            with self.subTest(content=content):
                if content is not None:
                    request.write_text(content, encoding="utf-8")
                plan = self.root / "invalid-plan.json"
                code, result = self.invoke("preview", request=request, plan=plan)
                self.assertEqual(code, 2, result)
                self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "invalid_input", False))
                self.assertFalse(plan.exists())
        self.assertEqual(self.snapshot(), original)

    def test_contextual_keyword_is_a_valid_local_name(self):
        line = self.source.read_text().splitlines()[5]
        code, result = self.preview(project=None, symbol=None, file=str(self.source), line=6,
                                    column=line.index("local") + 1, newName="record")
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertRegex(self.source.read_text(), r"int @?record = value; return @?record \+ Field;")
        self.run_dotnet("build", self.solution, "--no-restore", "--nologo")

    def test_request_directory_is_refused(self):
        original = self.snapshot()
        plan = self.root / "request-directory-plan.json"
        for command, options in [("inspect", {}), ("preview", {"plan": plan})]:
            with self.subTest(command=command):
                code, result = self.invoke(command, request=self.a, **options)
                self.assertEqual(code, 2, result)
                self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "invalid_input", False))
        self.assertFalse(plan.exists())
        self.assertEqual(self.snapshot(), original)

    def test_invalid_plan_input_is_refused(self):
        plan = self.root / "invalid-plan.json"
        code, result = self.invoke("apply", plan=plan)
        self.assertEqual(code, 2, result)
        self.assertEqual((result["status"], result["code"]), ("refused", "invalid_input"))
        payload = dict(contract="refactor-plan/1", edits=[],
                       request=dict(workspace=str(self.solution), symbol="T:Demo.Service", newName="Renamed"))
        for inputs in [[None], [{"path": str(self.source)}]]:
            with self.subTest(inputs=inputs):
                plan.write_text(json.dumps(payload | {"inputs": inputs}))
                code, result = self.invoke("apply", plan=plan)
                self.assertEqual(code, 2, result)
                self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "invalid_input", False))

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
        original = self.snapshot()
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "missing_file", False))
        self.assertIn("Missing.csproj", result["message"])
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_missing_solution_project_is_refused(self):
        self.solution.write_text('<Solution><Project Path="Missing.csproj" /></Solution>')
        original = self.snapshot()
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "missing_file", False))
        self.assertIn("Missing.csproj", result["message"])
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_missing_compile_input_is_refused(self):
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup><Compile Include="Missing.cs" /></ItemGroup></Project>'))
        original = self.snapshot()
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "missing_file", False))
        self.assertIn("Missing.cs", result["message"])
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_generated_relation(self):
        generated = self.a / "Generated.g.cs"
        generated.write_text("namespace Demo; class Generated : Service { public override int Get(int value) => base.Get(value); }")
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertIn(result["code"], ["uneditable_symbol", "uneditable_reference", "uneditable_source"])
        self.assertIn(".g.cs suffix", result["message"])
        self.assertIn(generated.name, result["message"])

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

    def test_unrelated_source_generator_output_is_allowed(self):
        (self.a / "Json.cs").write_text("using System.Text.Json.Serialization; [JsonSerializable(typeof(string))] internal partial class Context : JsonSerializerContext {}")
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)
        self.assertIn("service.Fetch(2)", self.consumer.read_text())
        self.run_dotnet("build", self.solution, "--no-restore", "--nologo")

    def test_source_generator_reference_and_declaration_are_refused(self):
        (self.a / "Json.cs").write_text("using System.Text.Json.Serialization; [JsonSerializable(typeof(Demo.Service))] internal partial class Context : JsonSerializerContext {}")
        original = self.snapshot()
        code, result = self.preview(symbol="P:Demo.Service.Property", newName="Value")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "uneditable_reference")
        self.assertIn("source-generator output", result["message"])
        self.assertFalse(self.plan_path.exists())
        code, result = self.preview(symbol="P:Context.Service", newName="ServiceInfo")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "uneditable_symbol")
        self.assertIn("source-generator output", result["message"])
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_external_sdk_intermediate_output_is_allowed(self):
        (self.root / "Directory.Build.props").write_text(
            '<Project><PropertyGroup><UseArtifactsOutput>true</UseArtifactsOutput>'
            '<ArtifactsPath>$(MSBuildThisFileDirectory)artifacts</ArtifactsPath></PropertyGroup></Project>'
        )
        self.restore()
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        inputs = [pathlib.Path(i["path"]) for i in plan["inputs"]]
        self.assertTrue(any(path.is_relative_to(self.root / "artifacts") and path.name.endswith("AssemblyAttributes.cs") for path in inputs))
        self.assertTrue(all(pathlib.Path(edit["path"]) in (self.source, self.consumer) for edit in plan["edits"]))
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)

    def test_ancestor_bin_is_not_a_generated_directory(self):
        ancestor = self.root / "bin"
        ancestor.mkdir()
        relocated = self.a.rename(ancestor / "A")
        self.project = relocated / self.project.name
        self.run_dotnet("restore", self.project, "--source", self.root, "-p:NuGetAudit=false")
        code, result = self.preview(workspace=str(self.project), symbol="F:Demo.Service.Field", newName="Data")
        self.assertEqual(code, 0, result)
        self.assertIn("Service.cs", str(result["files"]))

    def junction(self, path, target):
        env = os.environ | {"REFACTOR_TEST_LINK": str(path), "REFACTOR_TEST_TARGET": str(target)}
        run = subprocess.run(["pwsh", "-NoProfile", "-Command",
                              "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:REFACTOR_TEST_LINK -Target $env:REFACTOR_TEST_TARGET | Out-Null"],
                             env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_readonly_junction_inputs_are_canonical_and_retarget_is_drift(self):
        original_dir = self.root / "original-import"
        replacement_dir = self.root / "replacement-import"
        alias = self.root / "import-alias"
        for directory in (original_dir, replacement_dir):
            directory.mkdir()
            (directory / "Config.props").write_text("<Project />")
        self.junction(alias, original_dir)
        self.project.write_text(self.project.read_text().replace("</Project>",
            '<ItemGroup><AdditionalFiles Include="../import-alias/Config.props" /></ItemGroup></Project>'))
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        captured = next(i for i in plan["inputs"] if pathlib.Path(i["path"]) == alias / "Config.props")
        self.assertEqual(pathlib.Path(captured["canonicalPath"]).name, "Config.props")
        self.assertEqual(pathlib.Path(captured["canonicalPath"]).parent.name, original_dir.name)
        alias.rmdir()
        self.junction(alias, replacement_dir)
        original = self.snapshot()
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "input_drift")
        self.assertFalse(result["sourceWrites"])
        self.assertEqual(self.snapshot(), original)
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 0, result)

    def test_editable_source_and_plan_junctions_are_refused(self):
        target = self.root / "linked-source"
        target.mkdir()
        alias = self.root / "plan-alias"
        self.junction(alias, target)
        code, result = self.preview(plan_path=alias / "plan.json")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "linked_path")
        self.assertFalse(self.plan_path.exists())
        (target / "Extra.cs").write_text("public class Extra {}")
        self.junction(self.a / "alias", target)
        self.project.write_text(self.project.read_text().replace("</Project>",
            '<ItemGroup><Compile Remove="alias/**/*.cs" /><Compile Include="alias/Extra.cs" /></ItemGroup></Project>'))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "linked_path")
        self.assertFalse(self.plan_path.exists())

    def test_missing_canonical_input_is_refused_before_apply(self):
        target = self.root / "original-input"
        target.mkdir()
        config = target / "Config.props"
        config.write_text("<Project />")
        alias = self.root / "input-alias"
        self.junction(alias, target)
        self.project.write_text(self.project.read_text().replace("</Project>",
            '<ItemGroup><AdditionalFiles Include="../input-alias/Config.props" /></ItemGroup></Project>'))
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertTrue(next(i for i in plan["inputs"] if pathlib.Path(i["path"]) == alias / config.name)["canonicalPath"])
        config.unlink()
        original = self.snapshot()
        code, result = self.invoke("apply", plan=self.plan_path)
        self.assertEqual(code, 2, result)
        self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "apply_preflight_failed", False))
        self.assertIsNone(result.get("recovery"))
        self.assertEqual(self.snapshot(), original)

    def test_exclusively_locked_input_is_refused_before_apply(self):
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                      wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        original = self.snapshot()
        for path in [self.source, self.project]:
            with self.subTest(path=path):
                handle = kernel.CreateFileW(str(path), 0x80000000, 0, None, 3, 0x80, None)
                self.assertNotEqual(handle, ctypes.c_void_p(-1).value, ctypes.get_last_error())
                try:
                    code, result = self.invoke("apply", plan=self.plan_path)
                    self.assertEqual(code, 2, result)
                    self.assertEqual((result["status"], result["code"], result["sourceWrites"]), ("refused", "apply_preflight_failed", False))
                    self.assertIsNone(result.get("recovery"))
                finally:
                    self.assertTrue(kernel.CloseHandle(handle))
                self.assertEqual(self.snapshot(), original)

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

    def test_patch_keeps_separate_compact_hunks(self):
        padding = "".join(f"// unchanged {i}\n" for i in range(100))
        self.source.write_text("namespace Demo;\nclass Service { int field;\n" + padding +
                               "int Use() => field;\n}\n", newline="\n")
        self.consumer.write_text("public class Use {}")
        code, result = self.preview(symbol="F:Demo.Service.field", newName="data")
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        patch = plan["patch"]
        self.assertEqual(patch.count("\n@@ -"), 2)
        self.assertIn("-class Service { int field;\n+class Service { int data;\n", patch)
        self.assertIn("-int Use() => field;\n+int Use() => data;\n", patch)
        self.assertNotIn("// unchanged 50", patch)
        self.assertEqual(base64.b64decode(plan["edits"][0]["before"]), self.source.read_bytes())

    def test_patch_preserves_cr_only_payload(self):
        before = b"namespace Demo;\rclass Service {\r int value;\r int Use() => value;\r}\r"
        after = b"namespace Demo;\rclass Service {\r int data;\r int Use() => data;\r}\r"
        self.source.write_bytes(before)
        self.consumer.write_text("public class Use {}")
        code, result = self.preview(symbol="F:Demo.Service.value", newName="data")
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(len(plan["edits"]), 1)
        self.assertEqual(base64.b64decode(plan["edits"][0]["before"]), before)
        self.assertEqual(base64.b64decode(plan["edits"][0]["after"]), after)
        marker = b"\n\\ No newline at end of file\n"
        expected = b"--- a/A/Service.cs\n+++ b/A/Service.cs\n@@ -1,1 +1,1 @@\n-" + before + marker + b"+" + after + marker
        self.assertEqual(plan["patch"].encode("utf-8"), expected)

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

    def test_design_time_outside_source_refused(self):
        shared = self.root / "Shared.cs"
        shared.write_text("public class Shared { public Demo.Service Value = new(); }")
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup Condition="\'$(DesignTimeBuild)\' == \'true\'"><Compile Include="../Shared.cs" /></ItemGroup></Project>'))
        original = self.snapshot()
        code, result = self.preview(symbol="T:Demo.Service", newName="Renamed")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "linked_file")
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_design_time_extra_authored_source_refused(self):
        extra = self.a / "Extra.cs"
        extra.write_text("public class Extra { public Demo.Service Value = new(); }")
        self.project.write_text(self.project.read_text().replace("</Project>", '<ItemGroup><Compile Remove="Extra.cs" /><Compile Include="Extra.cs" Condition="\'$(DesignTimeBuild)\' == \'true\'" /></ItemGroup></Project>'))
        code, result = self.preview(symbol="T:Demo.Service", newName="Renamed")
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "unexpected_source")
        self.assertFalse(self.plan_path.exists())

    def test_design_time_missing_reference_edge_refused(self):
        project = self.b / "B.csproj"
        project.write_text(project.read_text().replace('<ProjectReference Include=', '<ProjectReference Condition="\'$(DesignTimeBuild)\' != \'true\'" Include='))
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "incomplete_references")
        self.assertFalse(self.plan_path.exists())

    def test_build_only_reference_is_not_a_compilation_edge(self):
        self.consumer.write_text("public class Use {}")
        project = self.b / "B.csproj"
        project.write_text(project.read_text().replace('<ProjectReference Include=', '<ProjectReference ReferenceOutputAssembly="false" Include='))
        code, result = self.preview()
        self.assertEqual(code, 0, result)
        plan = json.loads(self.plan_path.read_text())
        self.assertEqual(next(p for p in plan["projects"] if pathlib.Path(p["path"]) == project)["references"], [])

    def test_malformed_source_encoding_refused_without_writes(self):
        self.source.write_bytes(b'\xef\xbb\xbf' + self.source.read_bytes() + b'// malformed \xff\n')
        original = self.snapshot()
        code, result = self.preview()
        self.assertEqual(code, 2, result)
        self.assertEqual(result["code"], "lossy_encoding")
        self.assertFalse(self.plan_path.exists())
        self.assertEqual(self.snapshot(), original)

    def test_alias_and_generic_nameof_preserve_syntax(self):
        self.source.write_text('namespace Demo;\npublic class Plain { public string Name => nameof(global::Demo.Plain); }\npublic class Generic<T> { public string Name => nameof(Generic<T>); public string Open => nameof(Generic<>); }\n')
        self.consumer.write_text("public class Use {}")
        for symbol, name in [("T:Demo.Plain", "Renamed"), ("T:Demo.Generic`1", "RenamedGeneric")]:
            code, result = self.preview(symbol=symbol, newName=name)
            self.assertEqual(code, 0, result)
            code, result = self.invoke("apply", plan=self.plan_path)
            self.assertEqual(code, 0, result)
        source = self.source.read_text()
        self.assertIn("nameof(global::Demo.Renamed)", source)
        self.assertIn("nameof(RenamedGeneric<T>)", source)
        self.assertIn("nameof(RenamedGeneric<>)", source)
        self.run_dotnet("build", self.solution, "--no-restore", "--nologo")

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
