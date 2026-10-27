import hashlib
import json
from pathlib import Path
import unittest

from monkey.code_architecture_inheritance import (
    InheritanceEvidenceError,
    resolve_inherited_members,
)


ROOT = Path(__file__).resolve().parents[1]


def _row(class_id, name, namespace, path, source, *, kind="class"):
    raw = source.encode("utf-8") if isinstance(source, str) else source
    digest = hashlib.sha256(raw).hexdigest()
    return ({"classId": class_id, "name": name, "namespace": namespace, "kind": kind,
             "path": path, "sha256": digest, "bytes": len(raw)},
            {"path": path, "sha256": digest, "bytes": len(raw), "source": raw})


def _resolve(records, mappings, requirements, **kwargs):
    return resolve_inherited_members(records, mappings, requirements, **kwargs)["results"]


class CodeArchitectureInheritanceTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / '.private/v060-architecture-first-20261027/NativeCorePriority03/Modules/0036/architecture-module-manifest.json').is_file(), 'Optional private source audit is unavailable')
    def test_real_tutorial_module_resolves_only_hash_pinned_guideutil_members(self):
        module = ROOT / ".private/v060-architecture-first-20261027/NativeCorePriority03/Modules/0036"
        manifest_path = module / "architecture-module-manifest.json"
        manifest_raw = manifest_path.read_bytes()
        expected_manifest_sha = (module / "architecture-module-manifest.json.sha256").read_text().strip()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), expected_manifest_sha)
        manifest = json.loads(manifest_raw)
        rows = [row for row in manifest["classes"]
                if row.get("path", "").startswith("Assets/Game/Presentation/Tutorial/")
                and row.get("completenessDiagnostics")]
        self.assertEqual(len(rows), 15)

        records = []
        mappings = {}
        requirements = {}
        for row in rows:
            path = row["path"]
            source = (module / path).read_bytes()
            self.assertEqual(len(source), row["bytes"])
            self.assertEqual(hashlib.sha256(source).hexdigest(), row["sha256"])
            records.append({key: row[key] for key in ("classId", "name", "namespace", "kind", "path", "sha256", "bytes")})
            mappings[path] = {"path": path, "sha256": row["sha256"], "bytes": row["bytes"], "source": source}
            requirements[row["classId"]] = ["Bind", "Render", "OnEnable", "OnDisable", "OnDestroy",
                                                 "Controller", "Snapshot", "LifetimeCancellation"]

        guide_util = next(row for row in manifest["classes"] if row.get("classId") == "Tutorial.GuideUtil")
        guide_util_path = guide_util["path"]
        guide_util_source = (module / guide_util_path).read_bytes()
        self.assertEqual(hashlib.sha256(guide_util_source).hexdigest(), guide_util["sha256"])
        records.append({key: guide_util[key] for key in ("classId", "name", "namespace", "kind", "path", "sha256", "bytes")})
        mappings[guide_util_path] = {"path": guide_util_path, "sha256": guide_util["sha256"],
                                     "bytes": guide_util["bytes"], "source": guide_util_source}
        requirements[guide_util["classId"]] = ["Bind", "Render", "OnEnable", "OnDisable", "OnDestroy",
                                                "Controller", "Snapshot", "LifetimeCancellation"]

        results = _resolve(records, mappings, requirements)
        self.assertEqual(len(results), 16)
        by_id = {row["classId"]: row for row in results}
        for row in rows:
            result = by_id[row["classId"]]
            for member in requirements[row["classId"]]:
                self.assertTrue(result["requiredMembers"][member]["satisfied"], (row["classId"], member, result))
            self.assertIn("FoodStreet.Presentation.Tutorial.GuideUtil", [x["qualifiedName"] for x in result["baseShaChain"]])
            self.assertEqual(result["requiredMembers"]["Controller"]["sourceSha256"], guide_util["sha256"])
            self.assertEqual(result["requiredMembers"]["Bind"]["sourceSha256"], guide_util["sha256"])
        self.assertEqual(by_id["Tutorial.GuideHand"]["requiredMembers"]["Render"]["declaredBy"], "Tutorial.GuideHand")
        self.assertEqual(by_id["Tutorial.GuideUtil"]["requiredMembers"]["Snapshot"]["accessibility"], "public")

    @unittest.skipUnless((ROOT / '.private/v060-architecture-first-20261027/NativeProject01/Modules/0026/architecture-module-manifest.json').is_file(), 'Optional private source audit is unavailable')
    def test_real_narrative_items_resolve_only_hash_pinned_narrative_item_members(self):
        module = ROOT / ".private/v060-architecture-first-20261027/NativeProject01/Modules/0026"
        manifest_path = module / "architecture-module-manifest.json"
        manifest_raw = manifest_path.read_bytes()
        expected_manifest_sha = (module / "architecture-module-manifest.json.sha256").read_text().strip()
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), expected_manifest_sha)
        manifest = json.loads(manifest_raw)
        child_names = {
            "Narrative_DishItem", "Narrative_IllustrationItem",
            "Narrative_TalkItem", "Narrative_VOItem",
        }
        children = [row for row in manifest["classes"] if row.get("name") in child_names]
        self.assertEqual(len(children), 4)
        base = next(row for row in manifest["classes"] if row.get("classId") == "Narrative.NarrativeItem")
        records = []
        mappings = {}
        requirements = {}
        expected = [*children, base]
        required = ["Bind", "Render", "OnEnable", "OnDestroy", "Controller", "Snapshot", "LifetimeCancellation"]
        for row in expected:
            source = (module / row["path"]).read_bytes()
            self.assertEqual(len(source), row["bytes"])
            self.assertEqual(hashlib.sha256(source).hexdigest(), row["sha256"])
            records.append({key: row[key] for key in ("classId", "name", "namespace", "kind", "path", "sha256", "bytes")})
            mappings[row["path"]] = {"path": row["path"], "sha256": row["sha256"], "bytes": row["bytes"], "source": source}
            requirements[row["classId"]] = required

        results = _resolve(records, mappings, requirements)
        self.assertEqual(len(results), 5)
        by_id = {row["classId"]: row for row in results}
        for child in children:
            result = by_id[child["classId"]]
            for member in required:
                self.assertTrue(result["requiredMembers"][member]["satisfied"], (child["classId"], member, result))
            self.assertIn("FoodStreet.Presentation.Narrative.NarrativeItem",
                          [item["qualifiedName"] for item in result["baseShaChain"]])
            self.assertEqual(result["requiredMembers"]["Controller"]["sourceSha256"], base["sha256"])
            self.assertEqual(result["requiredMembers"]["Snapshot"]["sourceSha256"], base["sha256"])
            self.assertEqual(result["requiredMembers"]["LifetimeCancellation"]["sourceSha256"], base["sha256"])

    def test_conditional_parent_declarations_cannot_supply_inherited_members(self):
        parent, parent_map = _row('base','Base','Demo','Base.cs',
            'namespace Demo { public class Base {\n#if false\npublic void Bind() {}\n#endif\n} }')
        child, child_map = _row('child','Child','Demo','Child.cs',
            'namespace Demo { public class Child : Base { } }')
        result = _resolve([child,parent], {'Child.cs':child_map,'Base.cs':parent_map}, {'child':['Bind']})[0]
        self.assertFalse(result['requiredMembers']['Bind']['satisfied'])
        self.assertIn('conditional_compilation_unsupported', result['blockers'])

    def test_only_public_or_protected_direct_base_members_are_inherited(self):
        base_source = """namespace Demo { public class Base {
            public void Bind() { }
            protected int Snapshot;
            protected internal object Controller { get; set; }
            internal string InternalOnly;
            private void Hidden() { }
            private int LifetimeCancellation;
        } }
        """
        child_source = "namespace Demo { public class Child : Base { } }"
        base, base_map = _row("base", "Base", "Demo", "Base.cs", base_source)
        child, child_map = _row("child", "Child", "Demo", "Child.cs", child_source)
        result = _resolve([child, base], {"Base.cs": base_map, "Child.cs": child_map},
                          {"child": {"Bind": "method", "Snapshot": "field", "Controller": "property",
                                     "Hidden": "method", "LifetimeCancellation": "field", "InternalOnly": "field"}})[0]
        self.assertTrue(result["requiredMembers"]["Bind"]["satisfied"])
        self.assertTrue(result["requiredMembers"]["Snapshot"]["satisfied"])
        self.assertTrue(result["requiredMembers"]["Controller"]["satisfied"])
        self.assertFalse(result["requiredMembers"]["Hidden"]["satisfied"])
        self.assertFalse(result["requiredMembers"]["LifetimeCancellation"]["satisfied"])
        self.assertFalse(result["requiredMembers"]["InternalOnly"]["satisfied"])
        self.assertIn("private_declaration_not_inherited:Hidden", result["blockers"])

    def test_calls_comments_strings_and_nested_types_are_not_member_declarations(self):
        base_source = r'''namespace Demo {
          public class Base {
            private class Nested { public void Render() { } }
            public string Text = "public void Bind() { }";
            // protected void Snapshot();
            /* public void LifetimeCancellation(); */
            public void Run() { Render(); Bind(); Snapshot(); }
          }
        }'''
        child_source = r'''namespace Demo {
          public class Child : Base {
            public void RunAgain() { Bind(); Render(); }
            public string Text2 = "Snapshot LifetimeCancellation";
          }
        }'''
        base, base_map = _row("base", "Base", "Demo", "Base.cs", base_source)
        child, child_map = _row("child", "Child", "Demo", "Child.cs", child_source)
        result = _resolve([base, child], {"Base.cs": base_map, "Child.cs": child_map},
                          {"child": ["Bind", "Render", "Snapshot", "LifetimeCancellation"]})[1]
        for name, evidence in result["requiredMembers"].items():
            self.assertFalse(evidence["satisfied"], name)

    def test_unqualified_bases_resolve_only_in_same_namespace(self):
        other_source = "namespace Other { public class GuideUtil { public void Bind() { } } }"
        child_source = "namespace Demo { public class Child : GuideUtil { } }"
        other, other_map = _row("other", "GuideUtil", "Other", "Other.cs", other_source)
        child, child_map = _row("child", "Child", "Demo", "Child.cs", child_source)
        result = _resolve([other, child], {"Other.cs": other_map, "Child.cs": child_map}, {"child": ["Bind"]})[1]
        self.assertFalse(result["requiredMembers"]["Bind"]["satisfied"])
        self.assertIn("no_exact_class_record", [x["reason"] for x in result["unresolvedBases"]])

    def test_fully_qualified_base_is_exact_and_duplicate_qname_is_ambiguous(self):
        one, one_map = _row("one", "Base", "Demo", "One.cs", "namespace Demo { public class Base { public void Bind() { } } }")
        two, two_map = _row("two", "Base", "Demo", "Two.cs", "namespace Demo { public class Base { public void Render() { } } }")
        child, child_map = _row("child", "Child", "Demo", "Child.cs", "namespace Demo { public class Child : global::Demo.Base { } }")
        result = _resolve([one, two, child], {"One.cs": one_map, "Two.cs": two_map, "Child.cs": child_map},
                          {"child": ["Bind"]})[-1]
        self.assertFalse(result["requiredMembers"]["Bind"]["satisfied"])
        self.assertIn("ambiguous_base_class:Demo.Base", result["blockers"])

    def test_qualified_base_resolves_exactly_and_using_alias_does_not_override_it(self):
        base_source = "namespace Demo { public class Base { public void Bind() { } } }"
        child_source = "using Base = Other.Base; namespace Demo { public class Child : global::Demo.Base { } }"
        base, base_map = _row("base", "Base", "Demo", "Base.cs", base_source)
        child, child_map = _row("child", "Child", "Demo", "Child.cs", child_source)
        result = _resolve([child, base], {"Base.cs": base_map, "Child.cs": child_map}, {"child": ["Bind"]})[0]
        self.assertTrue(result["requiredMembers"]["Bind"]["satisfied"])

        alias_child_source = "using Base = Other.Base; namespace Demo { public class AliasChild : Base { } }"
        alias_child, alias_map = _row("alias", "AliasChild", "Demo", "Alias.cs", alias_child_source)
        alias_result = _resolve([alias_child, base], {"Alias.cs": alias_map, "Base.cs": base_map}, {"alias": ["Bind"]})[0]
        self.assertFalse(alias_result["requiredMembers"]["Bind"]["satisfied"])
        self.assertEqual(alias_result["unresolvedBases"][0]["reason"], "base_name_is_using_alias")

    def test_missing_source_hash_mismatch_cycle_depth_and_generic_boundaries(self):
        child, child_map = _row("child", "Child", "Demo", "Child.cs", "namespace Demo { public class Child : Missing { } }")
        missing = _resolve([child], {"Child.cs": child_map}, {"child": ["Bind"]})[0]
        self.assertEqual(missing["unresolvedBases"][0]["type"], "Missing")

        with self.assertRaisesRegex(InheritanceEvidenceError, "SHA-256 mismatch"):
            resolve_inherited_members([child], {"Child.cs": {**child_map, "sha256": "0" * 64}}, {"child": ["Bind"]})
        absent = _resolve([child], {}, {"child": ["Bind"]})[0]
        self.assertIn("missing_source_mapping", absent["blockers"])

        a, a_map = _row("a", "A", "Demo", "A.cs", "namespace Demo { public class A : B { } }")
        b, b_map = _row("b", "B", "Demo", "B.cs", "namespace Demo { public class B : A { } }")
        cycle = _resolve([a, b], {"A.cs": a_map, "B.cs": b_map}, {"a": ["Bind"]})[0]
        self.assertIn("inheritance_cycle", cycle["blockers"])
        depth = _resolve([a, b], {"A.cs": a_map, "B.cs": b_map}, {"a": ["Bind"]}, max_depth=1)[0]
        self.assertIn("maximum_inheritance_depth_exceeded", depth["blockers"])

        generic, generic_map = _row("generic", "GenericChild", "Demo", "Generic.cs",
                                    "namespace Demo { public class GenericChild<T> : A { } }")
        bounded = _resolve([generic, a], {"Generic.cs": generic_map, "A.cs": a_map}, {"generic": ["Bind"]})[0]
        self.assertIn("generic_class_unsupported", bounded["blockers"])
        self.assertFalse(bounded["requiredMembers"]["Bind"]["satisfied"])

        partial, partial_map = _row("partial", "PartialChild", "Demo", "Partial.cs",
                                    "namespace Demo { public partial class PartialChild : A { } }")
        partial_result = _resolve([partial, a], {"Partial.cs": partial_map, "A.cs": a_map}, {"partial": ["Bind"]})[0]
        self.assertIn("partial_class_unsupported", partial_result["blockers"])


if __name__ == "__main__":
    unittest.main()
