import unittest
import tempfile
import hashlib
from pathlib import Path

from monkey.code_graph import facts
from monkey.code_draft_render import render_field, render_method


def n(node_type, **values):
    return {"type": node_type, **values}


def ident(name):
    return n("Identifier", name=name)


class CodeDraftRenderTests(unittest.TestCase):
    def test_control_flow_calls_collections_math_string_and_callback_render_as_code(self):
        source = b'function update(x){ /* body */ }'
        ast = n("FunctionExpression", **{"async": False}, params=[ident("x")], body=n("BlockStatement", body=[
            n("IfStatement", test=ident("x"), consequent=n("BlockStatement", body=[
                n("ExpressionStatement", expression=n("AssignmentExpression", operator="+=", left=ident("x"), right=n("Literal", value=1)))
            ]), alternate=n("BlockStatement", body=[
                n("ExpressionStatement", expression=n("AssignmentExpression", operator="=", left=ident("x"), right=n("Literal", value=2)))
            ])),
            n("ForStatement", init=n("VariableDeclaration", kind="let", declarations=[n("VariableDeclarator", id=ident("i"), init=n("Literal", value=0))]),
              test=n("BinaryExpression", operator="<", left=ident("i"), right=n("Literal", value=2)),
              update=n("UpdateExpression", operator="++", prefix=False, argument=ident("i")),
              body=n("BlockStatement", body=[n("ExpressionStatement", expression=n("AssignmentExpression", operator="+=", left=ident("x"), right=ident("i")))])),
            n("WhileStatement", test=n("BinaryExpression", operator="<", left=ident("x"), right=n("Literal", value=10)),
              body=n("BlockStatement", body=[n("ExpressionStatement", expression=n("UpdateExpression", operator="++", prefix=False, argument=ident("x")))])),
            n("SwitchStatement", discriminant=ident("x"), cases=[
            n("SwitchCase", test=n("Literal", value=1), consequent=[
                    n("ExpressionStatement", expression=n("AssignmentExpression", operator="=", left=ident("x"), right=n("Literal", value=3))),
                    n("BreakStatement")]),
                n("SwitchCase", test=None, consequent=[n("ReturnStatement", argument=ident("x"))])]),
            n("TryStatement", block=n("BlockStatement", body=[n("ThrowStatement", argument=n("Literal", value="oops"))]),
              handler=n("CatchClause", param=ident("error"), body=n("BlockStatement", body=[n("ExpressionStatement", expression=n("CallExpression", callee=n("MemberExpression", computed=False, object=ident("cc"), property=ident("warn")), arguments=[ident("error")]))])),
              finalizer=n("BlockStatement", body=[n("ExpressionStatement", expression=n("CallExpression", callee=ident("cleanup"), arguments=[]))])),
            n("VariableDeclaration", kind="const", declarations=[n("VariableDeclarator", id=ident("values"), init=n("ArrayExpression", elements=[ident("x"), n("CallExpression", callee=n("MemberExpression", computed=False, object=ident("Math"), property=ident("max")), arguments=[ident("x"), n("Literal", value=4)])]))]),
            n("VariableDeclaration", kind="const", declarations=[n("VariableDeclarator", id=ident("record"), init=n("ObjectExpression", properties=[n("Property", kind="init", method=False, computed=False, key=ident("label"), value=n("TemplateLiteral", quasis=[n("TemplateElement", value={"cooked": "hp="}) , n("TemplateElement", value={"cooked": ""})], expressions=[ident("x")]))]))]),
            n("ExpressionStatement", expression=n("CallExpression", callee=n("MemberExpression", computed=False, object=ident("cc"), property=ident("log")), arguments=[ident("record")])),
            n("ExpressionStatement", expression=n("CallExpression", callee=n("MemberExpression", computed=False, object=ident("values"), property=ident("forEach")), arguments=[n("ArrowFunctionExpression", **{"async": False}, params=[ident("item")], body=n("UpdateExpression", operator="++", prefix=False, argument=ident("item")))])),
            n("ReturnStatement", argument=ident("values"))
        ]))
        result = render_method({"name": "update", "sourceBytes": {"start": 0, "end": len(source)}}, ast, source, class_name="HealthState")
        code = result["source"]
        for expected in ("public dynamic update(dynamic x)", "if (x)", "for (dynamic i = 0;", "while ((x < 10))", "switch (x)", "try", "throw new System.Exception", "catch (System.Exception", "finally", "new System.Collections.Generic.List<dynamic>", "System.Math.Max", "$\"hp={x}\"", "UnityEngine.Debug.LogWarning", "(dynamic item)", "return values;"):
            self.assertIn(expected, code)
        self.assertIn("System.Collections.Generic", result["usings"])
        self.assertIn("UnityEngine", result["usings"])
        self.assertTrue(result["draftOnly"])
        self.assertFalse(result["sourceExecuted"])
        self.assertTrue(any(d["code"] == "throw_approximation" for d in result["diagnostics"]))

    def test_unsupported_local_expression_is_escaped_and_following_statements_survive(self):
        source = b"function f(x){ weird*/operation(x); return x + 1; }"
        start = source.index(b"weird*/operation")
        end = source.index(b";", start)
        unsupported = n("FutureExpression", start=start, end=end)
        ast = n("FunctionExpression", params=[ident("x")], body=n("BlockStatement", body=[
            n("ExpressionStatement", expression=unsupported),
            n("ReturnStatement", argument=n("BinaryExpression", operator="+", left=ident("x"), right=n("Literal", value=1)))
        ]))
        result = render_method({"name": "f", "sourceBytes": {"start": 0, "end": len(source)}}, ast, source)
        code = result["source"]
        self.assertIn("draft omission FutureExpression", code)
        self.assertIn("weird* /operation", code)
        self.assertIn("NotImplementedException", code)
        self.assertIn("return (x + 1);", code)
        self.assertTrue(any(d["code"] == "unsupported_expression" for d in result["diagnostics"]))
        self.assertNotIn("weird*/operation(x); */", code)

    def test_async_unmapped_cc_api_and_csharp_member_collision_are_named(self):
        source = b"async function HealthState(x){ return await cc.remote(x); }"
        start = source.index(b"cc.remote")
        end = source.index(b")", start) + 1
        callee = n("MemberExpression", start=start, end=end, computed=False, object=ident("cc"), property=ident("remote"))
        ast = n("FunctionExpression", **{"async": True}, params=[ident("x")], body=n("BlockStatement", body=[
            n("ReturnStatement", argument=n("AwaitExpression", argument=n("CallExpression", callee=callee, arguments=[ident("x")])))
        ]))
        result = render_method({"name": "HealthState", "sourceBytes": {"start": 0, "end": len(source)}}, ast, source, class_name="HealthState")
        self.assertIn("Task<dynamic> HealthState_DraftMethod", result["source"])
        self.assertIn("await cc.remote(x)", result["source"])
        self.assertIn("unmapped_cc_api", {d["code"] for d in result["diagnostics"]})
        self.assertIn("method_name_class_collision", {d["code"] for d in result["diagnostics"]})
        self.assertIn("System.Threading.Tasks", result["usings"])

    def test_invalid_source_span_fails_without_silent_method_success(self):
        with self.assertRaisesRegex(ValueError, "sourceBytes"):
            render_method({"name": "bad", "sourceBytes": {"start": -1, "end": 4}},
                          n("FunctionExpression", params=[], body=n("BlockStatement", body=[])), b"x")
        with self.assertRaisesRegex(ValueError, "sourceSha256"):
            render_method({"name": "bad", "sourceBytes": {"start": 0, "end": 1}, "sourceSha256": "0" * 64},
                          n("FunctionExpression", params=[], body=n("BlockStatement", body=[])), b"x")

    def test_actual_acorn_method_ast_renders_from_exact_utf8_source(self):
        raw = 'var Box=(function(){function e(){};e.prototype.work=function(x){if(x<2){x++;}return Math.max(x,3);};return e;})();'.encode()
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            source = Path(directory) / "source.js"
            source.write_bytes(raw)
            index = facts(source)
            method = next(row for row in index["methods"] if row["name"] == "work")
            selected = facts(source, index["source"]["sha256"], [method["id"]])["selected"][0]
        result = render_method(method, selected["ast"], raw, class_name="Box")
        self.assertIn("if ((x < 2))", result["source"])
        self.assertIn("System.Math.Max", result["source"])
        self.assertTrue(result["sourceExecuted"] is False)

    def test_method_with_no_renderable_statement_is_explicitly_blocked(self):
        source = b"function unknown(x){futureSyntax(x); }"
        start = source.index(b"futureSyntax")
        end = source.index(b";", start)
        ast = n("FunctionExpression", params=[ident("x")], body=n("BlockStatement", body=[
            n("FutureStatement", start=start, end=end)
        ]))
        result = render_method({"name": "unknown", "sourceBytes": {"start": 0, "end": len(source)}}, ast, source)
        self.assertIn("NotImplementedException", result["source"])
        self.assertIn("empty_draft_body_blocked", {d["code"] for d in result["diagnostics"]})

    def test_field_literal_and_collection_initializer_reuse_expression_renderer(self):
        source = b'e.items = [1, "two"];'
        start = source.index(b"[1")
        end = source.index(b"]", start) + 1
        ast = n("ArrayExpression", start=start, end=end, elements=[n("Literal", value=1), n("Literal", value="two")])
        result = render_field({"name": "items", "static": True, "sourceBytes": {"start": 0, "end": len(source)}}, ast, source, class_name="Store")
        self.assertEqual(result["source"], 'public static dynamic items = new System.Collections.Generic.List<dynamic> { 1, "two" };')
        self.assertIn("System.Collections.Generic", result["usings"])
        self.assertTrue(result["draftOnly"])

    def test_field_missing_or_unsupported_initializer_never_defaults_to_success(self):
        source = b'e.unknown = new FutureType();'
        result = render_field({"name": "unknown", "static": True, "sourceBytes": {"start": 0, "end": len(source)}}, None, source)
        self.assertIn("Field initializer AST unavailable", result["source"])
        self.assertIn("field_initializer_missing", {d["code"] for d in result["diagnostics"]})
        start = source.index(b"new FutureType")
        end = len(source) - 1
        ast = n("FutureExpression", start=start, end=end)
        unsupported = render_field({"name": "unknown", "static": True, "sourceBytes": {"start": 0, "end": len(source)}}, ast, source)
        self.assertIn("FutureExpression", unsupported["source"])
        self.assertIn("NotImplementedException", unsupported["source"])
        self.assertIn("unsupported_expression", {d["code"] for d in unsupported["diagnostics"]})

    def test_acorn_multi_declarator_and_for_initializer_emit_one_dynamic_type(self):
        raw = b'var Model=(function(){function e(){};e.prototype.run=function(x){var a=1,b=2;for(var i=0,j=1;i<3;i++){a+=j;}return a+b+x;};return e;})();'
        with tempfile.TemporaryDirectory(dir="/private/tmp") as directory:
            source = Path(directory) / "source.js"
            source.write_bytes(raw)
            index = facts(source)
            method = next(row for row in index["methods"] if row["name"] == "run")
            ast = facts(source, index["source"]["sha256"], [method["id"]])["selected"][0]["ast"]
        result = render_method(method, ast, raw, class_name="Model")
        code = result["source"]
        self.assertIn("dynamic a = 1, b = 2;", code)
        self.assertIn("for (dynamic i = 0, j = 1; (i < 3); i++)", code)
        self.assertNotIn("dynamic j =", code)

    def test_field_this_is_retained_with_static_initializer_diagnostic(self):
        raw = b'e.owner = this.active;'
        start = raw.index(b"this")
        ast = n("MemberExpression", start=start, end=len(raw) - 1, computed=False,
                object=n("ThisExpression", start=start, end=start + 4),
                property=n("Identifier", name="active", start=start + 5, end=len(raw) - 1))
        result = render_field({"name": "owner", "static": True, "sourceBytes": {"start": 0, "end": len(raw)}}, ast, raw)
        self.assertIn("(this).active", result["source"])
        self.assertIn("field_initializer_this", {d["code"] for d in result["diagnostics"]})


if __name__ == "__main__":
    unittest.main()
