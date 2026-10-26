"""Best-effort JavaScript AST to C# draft method renderer.

This is a syntax-oriented renderer, not a JavaScript runtime or a semantic
equivalence checker. It keeps supported neighboring statements when one node
cannot be expressed, and labels every local approximation or omission.
"""
from __future__ import annotations

import json
import hashlib
import re
from typing import Any

MAX_NODES = 100_000
MAX_DEPTH = 192
MAX_RAW_COMMENT = 320

_CSHARP_KEYWORDS = set("""abstract as base bool break byte case catch char checked class const continue decimal default delegate do double dynamic else enum event explicit extern false finally fixed float for foreach goto if implicit in int interface internal is lock long namespace new null object operator out override params private protected public readonly ref return sbyte sealed short sizeof stackalloc static string struct switch this throw true try typeof uint ulong unchecked unsafe ushort using virtual void volatile while var""".split())
_BINARY = {"===": "==", "!==": "!=", "==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">=", "+": "+", "-": "-", "*": "*", "/": "/", "%": "%", "|": "|", "&": "&", "^": "^", "<<": "<<", ">>": ">>", "in": "in", "instanceof": "is"}
_MATH = {"abs": "Abs", "acos": "Acos", "asin": "Asin", "atan": "Atan", "atan2": "Atan2", "ceil": "Ceiling", "cos": "Cos", "exp": "Exp", "floor": "Floor", "log": "Log", "max": "Max", "min": "Min", "pow": "Pow", "round": "Round", "sin": "Sin", "sqrt": "Sqrt", "tan": "Tan", "trunc": "Truncate"}


def _identifier(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return "_draftName"
    value = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not value or value[0].isdigit():
        value = "_" + value
    return "@" + value if value in _CSHARP_KEYWORDS else value


def _qualified_identifier(value: Any) -> str | None:
    """Accept a dotted symbol path, but never pass arbitrary C# source through."""
    if not isinstance(value, str) or not value or any(not part for part in value.split(".")):
        return None
    if not all(re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", part) for part in value.split(".")):
        return None
    return ".".join(_identifier(part) for part in value.split("."))


def _target_identifier(node: Any, fallback: Any = None) -> str:
    if isinstance(node, dict):
        raw = node.get("_draftIdentifierTarget")
        mapped = _identifier(raw) if isinstance(raw, str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", raw) else None
        if mapped:
            return mapped
    return _identifier(fallback)


def _is_unambiguous_global_identifier(node: Any) -> bool:
    return (isinstance(node, dict) and node.get("type") == "Identifier"
            and node.get("bindingId") is None and not node.get("bindingAmbiguous")
            and not node.get("_draftIdentifierTarget"))


class _Renderer:
    def __init__(self, method: dict[str, Any], ast: dict[str, Any], raw: bytes, class_name: str | None):
        self.method = method
        self.ast = ast
        self.raw = raw
        self.class_name = class_name
        self.diagnostics: list[dict[str, Any]] = []
        self._diagnostic_keys: set[tuple[Any, ...]] = set()
        self.approx_types: set[str] = {"unknown JavaScript values are represented as dynamic"}
        self.members: set[str] = set()
        self.nodes = 0
        self.switch_depth = 0
        self.loop_depth = 0
        self.uses_unity = False
        self.uses_generic = False
        self.uses_tasks = False
        self.uses_linq = False
        self.embedded_functions: list[dict[str, Any]] = []
        self._embedded_ids: set[str] = set()

    def _embed_marker(self, node: Any) -> str:
        if not isinstance(node, dict):
            return ""
        function_id = node.get("draftFunctionId")
        if not isinstance(function_id, str) or not re.fullmatch(r"(?:method|function)@[A-Za-z0-9_.:/-]{1,160}", function_id):
            return ""
        marker = f"/* source-function:{function_id} */"
        if function_id not in self._embedded_ids:
            self._embedded_ids.add(function_id)
            self.embedded_functions.append({"id": function_id, "marker": marker, "kind": node.get("type")})
        return marker + " "

    def diagnose(self, node: Any, code: str, message: str, approximation: str | None = None) -> None:
        start = node.get("start") if isinstance(node, dict) else None
        end = node.get("end") if isinstance(node, dict) else None
        key = (code, start, end, message)
        if key in self._diagnostic_keys:
            return
        self._diagnostic_keys.add(key)
        row = {"code": code, "message": message}
        if type(start) is int and type(end) is int and 0 <= start <= end <= len(self.raw):
            row["sourceBytes"] = {"start": start, "end": end}
        if approximation:
            row["approximation"] = approximation
            self.approx_types.add(approximation)
        self.diagnostics.append(row)

    def snippet(self, node: Any) -> str:
        if not isinstance(node, dict):
            return ""
        start, end = node.get("start"), node.get("end")
        if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(self.raw):
            return ""
        return self.raw[start:end].decode("utf-8", errors="replace")

    def _comment(self, text: str) -> str:
        text = text.replace("*/", "* /").replace("\r", " ").replace("\n", " ")
        if len(text) > MAX_RAW_COMMENT:
            text = text[:MAX_RAW_COMMENT] + "…"
        return text

    def _unknown_expression(self, node: dict[str, Any], reason: str) -> str:
        kind = node.get("type", "unknown")
        self.diagnose(node, "unsupported_expression", f"{kind}: {reason}; retained source fragment as a comment", "reached placeholder throws NotImplementedException; enclosing statements continue")
        message = json.dumps(f"Unsupported source AST expression: {kind}", ensure_ascii=True)
        return f"((System.Func<dynamic>)(() => {{ /* draft omission {kind}: {self._comment(self.snippet(node))} */ throw new System.NotImplementedException({message}); }}))()"

    def expr(self, node: Any, depth: int = 0) -> str:
        self.nodes += 1
        if not isinstance(node, dict):
            return "null"
        if depth > MAX_DEPTH or self.nodes > MAX_NODES:
            return self._unknown_expression(node, "renderer depth/node budget exceeded")
        kind = node.get("type")
        try:
            if kind == "Identifier":
                name = node.get("name")
                raw_target = node.get("_draftIdentifierTarget")
                target = _identifier(raw_target) if isinstance(raw_target, str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", raw_target) else None
                if target:
                    return target
                if raw_target is not None:
                    self.diagnose(node, "invalid_identifier_target", "Injected identifier target is not a safe C# symbol path; source name is retained", "identifier target mapping ignored")
                has_binding = node.get("bindingId") is not None or bool(node.get("bindingAmbiguous"))
                if name == "undefined" and not has_binding:
                    self.diagnose(node, "undefined_approximation", "JavaScript undefined is approximated as C# null", "undefined-to-null")
                    return "null"
                if name == "NaN" and not has_binding:
                    return "double.NaN"
                if name == "Infinity" and not has_binding:
                    return "double.PositiveInfinity"
                if not isinstance(name, str):
                    return self._unknown_expression(node, "identifier has no name")
                return _identifier(name)
            if kind == "ThisExpression":
                static_owner = _qualified_identifier(node.get("_draftStaticThisOwner"))
                if static_owner:
                    return static_owner
                if node.get("_draftStaticThisOwner") is not None:
                    self.diagnose(node, "invalid_static_this_owner", "Injected static-this owner is not a safe qualified C# name; source this is retained", "static receiver may still be invalid in this context")
                return "this"
            if kind == "Literal":
                value = node.get("value")
                if value is None:
                    return "null"
                if value is True:
                    return "true"
                if value is False:
                    return "false"
                if isinstance(value, str):
                    return json.dumps(value, ensure_ascii=True)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
                        return "double.NaN" if value != value else ("double.NegativeInfinity" if value < 0 else "double.PositiveInfinity")
                    return repr(value)
                return self._unknown_expression(node, "literal kind is unsupported")
            if kind == "ArrayExpression":
                self.uses_generic = True
                values = []
                for element in node.get("elements", []):
                    if element is None:
                        values.append("null")
                        self.diagnose(node, "array_hole_approximation", "Sparse array hole is represented as null", "sparse-array-hole-to-null")
                    elif element.get("type") == "SpreadElement":
                        values.append(self._unknown_expression(element, "spread element is not expanded"))
                    else:
                        values.append(self.expr(element, depth + 1))
                return "new System.Collections.Generic.List<dynamic> { " + ", ".join(values) + " }"
            if kind == "ObjectExpression":
                self.uses_generic = True
                pairs = []
                for prop in node.get("properties", []):
                    if prop.get("type") != "Property" or prop.get("kind", "init") != "init" or prop.get("method") or prop.get("computed"):
                        self.diagnose(prop, "object_member_approximation", "Computed, accessor, spread, or method property is retained only as a localized placeholder", "object entries include only ordinary key/value pairs")
                        continue
                    key_node = prop.get("key", {})
                    key = key_node.get("name") if key_node.get("type") == "Identifier" else key_node.get("value")
                    if not isinstance(key, str):
                        key = str(key)
                    pairs.append("[" + json.dumps(key, ensure_ascii=True) + "] = " + self.expr(prop.get("value"), depth + 1))
                return "new System.Collections.Generic.Dictionary<string, dynamic> { " + ", ".join(pairs) + " }"
            if kind == "MemberExpression":
                mapping = node.get("_draftMember")
                unresolved = node.get("_draftUnresolvedMember")
                prop = node.get("property", {})
                if isinstance(mapping, dict):
                    target_name = _target_identifier({}, mapping.get("name")) if isinstance(mapping.get("name"), str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", mapping.get("name")) else None
                    receiver = mapping.get("receiver")
                    if target_name and receiver == "static_owner":
                        owner = _qualified_identifier(mapping.get("ownerClass"))
                        if owner:
                            return owner + "." + target_name
                    elif target_name and receiver == "source":
                        return f"({self.expr(node.get('object'), depth + 1)}).{target_name}"
                    self.diagnose(node, "invalid_member_mapping", "Injected member mapping is incomplete or unsafe; source receiver/member is retained", "member target mapping ignored")
                if unresolved is not None:
                    reason = unresolved.get("reason") if isinstance(unresolved, dict) else str(unresolved)
                    self.diagnose(node, "unresolved_member_mapping", f"Member mapping unresolved: {reason or 'unspecified'}; original receiver and member are retained", "source-shaped member may not exist in target")
                obj = self.expr(node.get("object"), depth + 1)
                if node.get("computed"):
                    if isinstance(mapping, dict):
                        target_name = _target_identifier({}, mapping.get("name")) if isinstance(mapping.get("name"), str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", mapping.get("name")) else None
                        receiver = mapping.get("receiver")
                        if target_name and receiver == "source":
                            return f"({obj}).{target_name}"
                        if target_name and receiver == "static_owner":
                            owner = _qualified_identifier(mapping.get("ownerClass"))
                            if owner:
                                return owner + "." + target_name
                    return f"({obj})[{self.expr(prop, depth + 1)}]"
                name = prop.get("name") if isinstance(prop, dict) else None
                if not isinstance(name, str):
                    return self._unknown_expression(node, "member name is not static")
                original_object = node.get("object")
                static_this_owner = (_qualified_identifier(original_object.get("_draftStaticThisOwner"))
                                     if isinstance(original_object, dict) and original_object.get("type") == "ThisExpression"
                                     else None)
                if unresolved is not None and static_this_owner and not node.get("computed"):
                    return static_this_owner + "." + _identifier(name)
                obj_node = node.get("object", {})
                is_global_obj = _is_unambiguous_global_identifier(obj_node)
                if obj == "Math" and is_global_obj:
                    return "System.Math." + _MATH.get(name, _identifier(name))
                if obj == "cc" and is_global_obj:
                    return "cc." + _identifier(name)
                return f"({obj}).{_identifier(name)}"
            if kind == "CallExpression":
                callee = node.get("callee", {})
                args = [self.expr(arg, depth + 1) if arg.get("type") != "SpreadElement" else self._unknown_expression(arg, "spread call argument") for arg in node.get("arguments", [])]
                if callee.get("type") == "MemberExpression" and not callee.get("computed") and not callee.get("_draftMember") and not callee.get("_draftUnresolvedMember"):
                    obj = callee.get("object", {})
                    prop = callee.get("property", {}).get("name")
                    obj_unbound = _is_unambiguous_global_identifier(obj)
                    if obj_unbound and obj.get("name") == "Math" and isinstance(prop, str):
                        if prop == "random":
                            self.uses_unity = True
                            self.diagnose(node, "math_random_approximation", "Math.random maps to UnityEngine.Random.value", "Unity random source differs from JavaScript Math.random")
                            return "UnityEngine.Random.value"
                        if prop in _MATH:
                            return "System.Math." + _MATH[prop] + "(" + ", ".join(args) + ")"
                    if obj_unbound and obj.get("name") == "cc" and isinstance(prop, str):
                        mapped = {"log": "Debug.Log", "warn": "Debug.LogWarning", "error": "Debug.LogError"}.get(prop)
                        if mapped:
                            self.uses_unity = True
                            return "UnityEngine." + mapped + "(" + ", ".join(args) + ")"
                        if prop == "isValid" and args:
                            self.diagnose(node, "cc_is_valid_approximation", "cc.isValid is approximated by a null check", "Unity destroyed-object semantics are not included")
                            return "(" + args[0] + " != null)"
                        if prop in ("v2", "v3"):
                            self.uses_unity = True
                            target = "Vector2" if prop == "v2" else "Vector3"
                            return "new UnityEngine." + target + "(" + ", ".join(args) + ")"
                        self.diagnose(node, "unmapped_cc_api", f"cc.{prop} has no approved Unity API mapping", "retained as a source-shaped call; target API may be missing")
                return self.expr(callee, depth + 1) + "(" + ", ".join(args) + ")"
            if kind == "NewExpression":
                callee = node.get("callee", {})
                arguments = node.get("arguments", [])
                collection = callee.get("name") if _is_unambiguous_global_identifier(callee) else None
                if collection in ("Array", "Map", "Set"):
                    self.uses_generic = True
                    spread = any(isinstance(arg, dict) and arg.get("type") == "SpreadElement" for arg in arguments)
                    if spread or (collection in ("Map", "Set") and len(arguments) > 1):
                        evaluated = []
                        for arg in arguments:
                            if isinstance(arg, dict) and arg.get("type") == "SpreadElement":
                                self.diagnose(arg, "collection_spread_approximation", f"Spread argument to {collection} is evaluated but not expanded", "collection constructor throws after all arguments are evaluated")
                                evaluated.append(self.expr(arg.get("argument"), depth + 1))
                            else:
                                evaluated.append(self.expr(arg, depth + 1))
                        self.diagnose(node, "unknown_collection_constructor_shape", f"JavaScript {collection} constructor shape is not modeled; every argument is evaluated before an explicit throw", "collection construction omitted after preserving argument evaluation")
                        prelude = " ".join(f"dynamic __draftArg{i} = {value};" for i, value in enumerate(evaluated))
                        return f"((System.Func<dynamic>)(() => {{ {prelude} throw new System.NotImplementedException(\"Unsupported {collection} constructor shape\"); }}))()"
                    args = [self.expr(arg, depth + 1) for arg in arguments]
                    self.diagnose(node, "collection_constructor_approximation", f"JavaScript {collection} is lowered to a .NET generic collection with argument evaluation retained", "iteration, ordering, equality, coercion, or size limits may differ")
                    if collection == "Array":
                        if not args:
                            return "new System.Collections.Generic.List<dynamic>()"
                        if len(args) > 1:
                            return "new System.Collections.Generic.List<dynamic> { " + ", ".join(args) + " }"
                        self.uses_linq = True
                        return (
                            "((System.Func<dynamic>)(() => { dynamic __draftArrayArg = " + args[0] + "; "
                            "if (__draftArrayArg is byte || __draftArrayArg is sbyte || __draftArrayArg is short || __draftArrayArg is ushort || __draftArrayArg is int || __draftArrayArg is uint || __draftArrayArg is long || __draftArrayArg is ulong || __draftArrayArg is float || __draftArrayArg is double || __draftArrayArg is decimal) { "
                            "double __draftArrayLength = System.Convert.ToDouble(__draftArrayArg); "
                            "if (__draftArrayLength < 0 || __draftArrayLength > 1000000 || System.Math.Truncate(__draftArrayLength) != __draftArrayLength) throw new System.ArgumentOutOfRangeException(\"Array length\"); "
                            "return System.Linq.Enumerable.Repeat<dynamic>(null, (int)__draftArrayLength).ToList(); } "
                            "return new System.Collections.Generic.List<dynamic> { __draftArrayArg }; }))()"
                        )
                    if collection == "Map":
                        if not args:
                            return "new System.Collections.Generic.Dictionary<dynamic, dynamic>()"
                        return (
                            "((System.Func<dynamic>)(() => { dynamic __draftMapSource = " + args[0] + "; "
                            "var __draftMap = new System.Collections.Generic.Dictionary<dynamic, dynamic>(); "
                            "if (__draftMapSource == null) return __draftMap; "
                            "foreach (dynamic __draftPair in (System.Collections.IEnumerable)__draftMapSource) __draftMap[__draftPair[0]] = __draftPair[1]; "
                            "return __draftMap; }))()"
                        )
                    if not args:
                        return "new System.Collections.Generic.HashSet<dynamic>()"
                    return (
                        "((System.Func<dynamic>)(() => { dynamic __draftSetSource = " + args[0] + "; "
                        "var __draftSet = new System.Collections.Generic.HashSet<dynamic>(); "
                            "if (__draftSetSource == null) return __draftSet; "
                        "foreach (dynamic __draftSetItem in (System.Collections.IEnumerable)__draftSetSource) __draftSet.Add(__draftSetItem); "
                        "return __draftSet; }))()"
                    )
                args = [self.expr(arg, depth + 1) for arg in arguments]
                return "new " + self.expr(callee, depth + 1) + "(" + ", ".join(args) + ")"
            if kind == "BinaryExpression":
                op = node.get("operator")
                left, right = self.expr(node.get("left"), depth + 1), self.expr(node.get("right"), depth + 1)
                if op == "**":
                    return f"System.Math.Pow({left}, {right})"
                if op == "instanceof":
                    self.diagnose(node, "instanceof_approximation", "JavaScript instanceof is represented by C# pattern matching", "prototype chain semantics differ")
                    return f"({left} is {right})"
                if op == "in":
                    self.diagnose(node, "in_approximation", "JavaScript property membership is represented by IDictionary.ContainsKey", "prototype-chain membership is not represented")
                    return f"(({right}) is System.Collections.IDictionary __draftDict && __draftDict.Contains({left}))"
                if op in ("===", "!=="):
                    self.diagnose(node, "strict_equality_approximation", f"JavaScript {op} maps to C# { _BINARY[op] }", "dynamic binder/type coercion may differ")
                if op not in _BINARY:
                    return self._unknown_expression(node, f"binary operator {op!r} has no renderer")
                return f"({left} {_BINARY[op]} {right})"
            if kind == "LogicalExpression":
                op = node.get("operator")
                if op not in ("&&", "||", "??"):
                    return self._unknown_expression(node, f"logical operator {op!r} has no renderer")
                if op == "??":
                    self.diagnose(node, "nullish_approximation", "Nullish coalescing is represented by C# null-coalescing", "JavaScript undefined and null are both represented as null")
                    op = "??"
                else:
                    self.diagnose(node, "truthiness_approximation", f"JavaScript {op} is represented by C# boolean short-circuit", "JavaScript truthiness conversion is not inserted")
                return f"({self.expr(node.get('left'), depth + 1)} {op} {self.expr(node.get('right'), depth + 1)})"
            if kind == "AssignmentExpression":
                op = node.get("operator", "=")
                if op not in ("=", "+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>=", "||=", "&&=", "??="):
                    return self._unknown_expression(node, f"assignment operator {op!r} has no renderer")
                if op in ("||=", "&&=", "??="):
                    self.diagnose(node, "logical_assignment_approximation", f"JavaScript {op} maps to C# short-circuit assignment", "truthiness and undefined behavior differ")
                left = self.expr(node.get("left"), depth + 1)
                self.members.add(left)
                if op in ("||=", "&&=", "??="):
                    logical = {"||=": "||", "&&=": "&&", "??=": "??"}[op]
                    return f"({left} = ({left} {logical} {self.expr(node.get('right'), depth + 1)}))"
                return f"({left} {op} {self.expr(node.get('right'), depth + 1)})"
            if kind == "UpdateExpression":
                arg = self.expr(node.get("argument"), depth + 1)
                self.members.add(arg)
                return f"({node.get('operator', '++')}{arg})" if node.get("prefix") else f"({arg}{node.get('operator', '++')})"
            if kind == "UnaryExpression":
                op = node.get("operator")
                arg = self.expr(node.get("argument"), depth + 1)
                if op in ("!", "+", "-", "~"):
                    if op == "!":
                        self.diagnose(node, "truthiness_approximation", "JavaScript unary ! maps to C# boolean negation", "dynamic truthiness conversion is not inserted")
                    return f"({op}{arg})"
                if op == "typeof":
                    self.diagnose(node, "typeof_approximation", "typeof is approximated by the runtime CLR type name", "JavaScript type strings are not preserved")
                    return f"((object)({arg}) == null ? \"undefined\" : ((object)({arg})).GetType().Name)"
                if op == "void":
                    self.diagnose(node, "void_approximation", "void expression evaluates its operand then produces null", "comma-expression helper is not required for common expression statements")
                    return f"((System.Func<dynamic>)(() => {{ var __draftValue = {arg}; return null; }}))()"
                if op == "delete":
                    return self._unknown_expression(node, "delete mutates dynamic object shape and has no generic C# form")
                return self._unknown_expression(node, f"unary operator {op!r} has no renderer")
            if kind == "ConditionalExpression":
                self.diagnose(node, "conditional_truthiness_approximation", "Conditional test uses C# bool conversion", "JavaScript truthiness is not inserted")
                return f"({self.expr(node.get('test'), depth + 1)} ? {self.expr(node.get('consequent'), depth + 1)} : {self.expr(node.get('alternate'), depth + 1)})"
            if kind == "SequenceExpression":
                expressions = node.get("expressions", [])
                if not expressions:
                    return "null"
                rendered = [self.expr(item, depth + 1) for item in expressions]
                self.diagnose(node, "sequence_expression_approximation", "Comma expression is lowered to an immediately invoked lambda", "dynamic evaluation order is retained but debugger shape differs")
                prelude = " ".join("_ = " + item + ";" for item in rendered[:-1])
                return f"((System.Func<dynamic>)(() => {{ {prelude} return {rendered[-1]}; }}))()"
            if kind in ("ArrowFunctionExpression", "FunctionExpression"):
                params, init = self.parameters(node.get("params", []), node)
                body = node.get("body")
                if body and body.get("type") == "BlockStatement":
                    statements = self.block_contents(body, 0)
                    body_text = "{ " + " ".join(statements) + " }"
                else:
                    body_text = "=> " + self.expr(body, depth + 1)
                if init:
                    self.diagnose(node, "destructured_callback_parameter", "Destructured callback argument uses generated dynamic placeholder", "binding shape is not reconstructed")
                return self._embed_marker(node) + "(" + ", ".join(params) + ") => " + body_text
            if kind == "AwaitExpression":
                self.uses_tasks = True
                self.diagnose(node, "await_approximation", "await is emitted in a Task<dynamic> draft method", "Unity synchronization context and promise semantics are unverified")
                return "await " + self.expr(node.get("argument"), depth + 1)
            if kind == "TemplateLiteral":
                chunks = []
                quasis = node.get("quasis", [])
                exprs = node.get("expressions", [])
                for index, quasi in enumerate(quasis):
                    raw = quasi.get("value", {}).get("cooked")
                    if raw is None:
                        raw = quasi.get("value", {}).get("raw", "")
                    text = str(raw).replace("\\", "\\\\").replace('"', '\\"').replace("{", "{{").replace("}", "}}")
                    chunks.append(text)
                    if index < len(exprs):
                        chunks.append("{" + self.expr(exprs[index], depth + 1) + "}")
                return '$"' + "".join(chunks) + '"'
            if kind == "ChainExpression":
                self.diagnose(node, "optional_chain_approximation", "Optional-chain wrapper is removed", "null short-circuit behavior may differ")
                return self.expr(node.get("expression"), depth + 1)
            if kind in ("SpreadElement", "RestElement", "AssignmentPattern", "ObjectPattern", "ArrayPattern", "MetaProperty", "ImportExpression", "Super"):
                return self._unknown_expression(node, f"AST node {kind} is not representable in this method subset")
            return self._unknown_expression(node, f"AST node {kind!r} is not supported")
        except (KeyError, TypeError, ValueError, RecursionError):
            return self._unknown_expression(node, "malformed or over-nested AST node")

    def parameters(self, params: list[Any], owner: Any) -> tuple[list[str], list[str]]:
        rendered: list[str] = []
        setup: list[str] = []
        for index, param in enumerate(params):
            if isinstance(param, dict) and param.get("type") == "Identifier":
                rendered.append("dynamic " + _target_identifier(param, param.get("name")))
            elif isinstance(param, dict) and param.get("type") == "AssignmentPattern" and param.get("left", {}).get("type") == "Identifier":
                name = _target_identifier(param["left"], param["left"].get("name"))
                rendered.append("dynamic " + name)
                setup.append("// Draft note: JS default parameter retained at declaration source; invocation semantics are not reproduced.")
                self.diagnose(param, "default_parameter_approximation", "JavaScript default parameter is represented as a required dynamic argument", "optional call default not applied")
            elif isinstance(param, dict) and param.get("type") == "RestElement" and param.get("argument", {}).get("type") == "Identifier":
                name = _target_identifier(param["argument"], param["argument"].get("name"))
                rendered.append("params dynamic[] " + name)
                self.diagnose(param, "rest_parameter_approximation", "JavaScript rest parameter maps to params dynamic[]", "array identity and argument coercion may differ")
            else:
                name = f"__draftArg{index}"
                rendered.append("dynamic " + name)
                setup.append("// Draft note: destructuring/default binding from this parameter was not reconstructed: " + self._comment(self.snippet(param)))
                self.diagnose(param, "parameter_pattern_approximation", "Non-identifier parameter is retained as a dynamic placeholder", "parameter binding shape is omitted")
        return rendered, setup

    def declaration(self, node: dict[str, Any], *, inline: bool = False) -> list[str] | str:
        kind = node.get("kind", "var")
        declarators = []
        comments = []
        for decl in node.get("declarations", []):
            ident = decl.get("id", {})
            if ident.get("type") == "Identifier":
                name = _target_identifier(ident, ident.get("name"))
                init = self.expr(decl.get("init")) if decl.get("init") else "null"
                if decl.get("init") is None:
                    self.diagnose(decl, "uninitialized_local_approximation", "Uninitialized JavaScript local is initialized to null in the draft", "undefined-to-null")
                declarators.append(name + " = " + init)
            else:
                text = self._comment(self.snippet(decl))
                self.diagnose(decl, "destructuring_local_omitted", "Destructuring declaration could not be lowered; source fragment is retained", "subsequent declarations continue")
                comments.append("/* draft omission: " + text + " */")
        if kind in ("let", "const"):
            self.diagnose(node, "javascript_local_scope_approximation", f"JavaScript {kind} declaration maps to a C# dynamic local", "block reassignment and const enforcement may differ")
        if inline:
            if not declarators:
                return " ".join(comments)
            return " ".join(comments + ["dynamic " + ", ".join(declarators)])
        lines = list(comments)
        if declarators:
            lines.append("dynamic " + ", ".join(declarators) + ";")
        return lines

    def effect_expr(self, node: dict[str, Any]) -> str:
        rendered = self.expr(node)
        if node.get("type") in ("AssignmentExpression", "UpdateExpression") and rendered.startswith("(") and rendered.endswith(")"):
            return rendered[1:-1]
        return rendered

    def block_contents(self, node: dict[str, Any], level: int) -> list[str]:
        body = node.get("body", [])
        result: list[str] = []
        for child in body:
            result.extend(self.stmt(child, level))
        return result

    def stmt(self, node: Any, level: int = 1, depth: int = 0) -> list[str]:
        self.nodes += 1
        if not isinstance(node, dict):
            return []
        pad = "    " * max(1, min(level, 32))
        if depth > MAX_DEPTH or self.nodes > MAX_NODES:
            kind = node.get("type", "unknown")
            self.diagnose(node, "renderer_budget_omission", f"{kind} omitted after method renderer budget; sibling statements continue", "local source comment only")
            return [pad + "// Draft omission after renderer budget: " + self._comment(self.snippet(node))]
        kind = node.get("type")
        try:
            if kind == "BlockStatement":
                lines = [pad + "{"]
                for child in node.get("body", []):
                    lines.extend(self.stmt(child, level + 1, depth + 1))
                lines.append(pad + "}")
                return lines
            if kind == "EmptyStatement":
                return [pad + ";"]
            if kind == "ExpressionStatement":
                expression = node.get("expression", {})
                rendered = self.effect_expr(expression)
                if expression.get("type") in ("AssignmentExpression", "UpdateExpression", "CallExpression", "NewExpression", "AwaitExpression"):
                    return [pad + rendered + ";"]
                return [pad + "_ = " + rendered + ";"]
            if kind == "VariableDeclaration":
                return [pad + line for line in self.declaration(node)]
            if kind == "ReturnStatement":
                arg = node.get("argument")
                if arg is None:
                    self.diagnose(node, "undefined_return_approximation", "Bare JavaScript return is represented as return null", "undefined-to-null")
                    return [pad + "return null;"]
                return [pad + "return " + self.expr(arg, depth + 1) + ";"]
            if kind == "ThrowStatement":
                self.diagnose(node, "throw_approximation", "Thrown JavaScript values are wrapped in System.Exception", "primitive/object throw identity is not preserved")
                return [pad + "throw new System.Exception(System.Convert.ToString(" + self.expr(node.get("argument"), depth + 1) + "));" ]
            if kind == "IfStatement":
                self.diagnose(node, "truthiness_approximation", "if test uses C# dynamic-to-bool conversion", "JavaScript truthiness conversion is not inserted")
                lines = [pad + "if (" + self.expr(node.get("test"), depth + 1) + ")"]
                lines.extend(self.stmt(node.get("consequent"), level, depth + 1))
                if node.get("alternate"):
                    lines.append(pad + "else")
                    lines.extend(self.stmt(node["alternate"], level, depth + 1))
                return lines
            if kind == "SwitchStatement":
                self.switch_depth += 1
                lines = [pad + "switch (" + self.expr(node.get("discriminant"), depth + 1) + ")", pad + "{"]
                cases = node.get("cases", [])
                for index, case in enumerate(cases):
                    test = case.get("test")
                    if test is None:
                        lines.append(pad + "    default:")
                    else:
                        lines.append(pad + "    case " + self.expr(test, depth + 1) + ":")
                    lines.append(pad + "    {")
                    body = case.get("consequent", [])
                    for child in body:
                        lines.extend(self.stmt(child, level + 2, depth + 1))
                    last = next((child for child in reversed(body) if child.get("type") not in ("EmptyStatement",)), None)
                    if index < len(cases) - 1 and (last is None or last.get("type") not in ("BreakStatement", "ReturnStatement", "ThrowStatement", "ContinueStatement")):
                        next_case = cases[index + 1].get("test")
                        if next_case is not None and next_case.get("type") == "Literal" and isinstance(next_case.get("value"), (str, int, bool)):
                            lines.append(pad + "        goto case " + self.expr(next_case, depth + 1) + ";")
                        elif next_case is None:
                            lines.append(pad + "        goto default;")
                        else:
                            self.diagnose(case, "switch_fallthrough_approximation", "Dynamic case fall-through cannot be expressed as a C# goto case", "fall-through edge omitted")
                    lines.append(pad + "    }")
                lines.append(pad + "}")
                self.switch_depth -= 1
                return lines
            if kind == "ForStatement":
                init = node.get("init")
                init_text = ""
                if init:
                    init_text = self.declaration(init, inline=True) if init.get("type") == "VariableDeclaration" else self.effect_expr(init)
                test = self.expr(node["test"], depth + 1) if node.get("test") else "true"
                update = self.effect_expr(node["update"]) if node.get("update") else ""
                self.loop_depth += 1
                lines = [pad + f"for ({init_text}; {test}; {update})"]
                lines.extend(self.stmt(node.get("body"), level, depth + 1))
                self.loop_depth -= 1
                self.diagnose(node, "for_scope_approximation", "JavaScript for-loop locals are represented as dynamic C# locals", "closure capture and let-per-iteration binding differ")
                return lines
            if kind == "WhileStatement":
                self.loop_depth += 1
                lines = [pad + "while (" + self.expr(node.get("test"), depth + 1) + ")"]
                lines.extend(self.stmt(node.get("body"), level, depth + 1))
                self.loop_depth -= 1
                self.diagnose(node, "truthiness_approximation", "while test uses C# dynamic-to-bool conversion", "JavaScript truthiness conversion is not inserted")
                return lines
            if kind == "DoWhileStatement":
                self.loop_depth += 1
                lines = [pad + "do"]
                lines.extend(self.stmt(node.get("body"), level, depth + 1))
                lines.append(pad + "while (" + self.expr(node.get("test"), depth + 1) + ");")
                self.loop_depth -= 1
                self.diagnose(node, "truthiness_approximation", "do-while test uses C# dynamic-to-bool conversion", "JavaScript truthiness conversion is not inserted")
                return lines
            if kind in ("ForOfStatement", "ForInStatement"):
                left = node.get("left", {})
                if left.get("type") == "VariableDeclaration":
                    names = left.get("declarations", [{}])[0].get("id", {})
                    variable = _target_identifier(names, names.get("name")) if names.get("type") == "Identifier" else "__draftItem"
                else:
                    variable = self.expr(left, depth + 1)
                right = self.expr(node.get("right"), depth + 1)
                if kind == "ForInStatement":
                    right = "(" + right + ").Keys"
                    self.diagnose(node, "for_in_approximation", "for-in enumerates IDictionary.Keys", "JavaScript prototype enumeration is not represented")
                else:
                    self.diagnose(node, "for_of_approximation", "for-of maps to C# foreach", "JavaScript iterator protocol is not represented")
                self.loop_depth += 1
                lines = [pad + f"foreach (dynamic {variable} in {right})"]
                lines.extend(self.stmt(node.get("body"), level, depth + 1))
                self.loop_depth -= 1
                return lines
            if kind == "BreakStatement":
                return [pad + "break;"]
            if kind == "ContinueStatement":
                return [pad + "continue;"]
            if kind == "TryStatement":
                lines = [pad + "try"]
                lines.extend(self.stmt(node.get("block"), level, depth + 1))
                handler = node.get("handler")
                if handler:
                    param = handler.get("param")
                    lines.append(pad + "catch (System.Exception __draftException)")
                    lines.append(pad + "{")
                    if param and param.get("type") == "Identifier":
                        lines.append(pad + "    dynamic " + _target_identifier(param, param.get("name")) + " = __draftException;")
                    elif param:
                        lines.append(pad + "    // Draft omission: catch binding pattern " + self._comment(self.snippet(param)))
                        self.diagnose(param, "catch_pattern_approximation", "Catch destructuring binding is not reconstructed", "exception remains available as __draftException")
                    lines.extend(self.block_contents(handler.get("body", {}), level + 1))
                    lines.append(pad + "}")
                    self.diagnose(handler, "catch_approximation", "JavaScript catch receives any thrown value; C# catches System.Exception", "non-Exception JavaScript values are wrapped at emitted throw sites only")
                finalizer = node.get("finalizer")
                if finalizer:
                    lines.append(pad + "finally")
                    lines.extend(self.stmt(finalizer, level, depth + 1))
                return lines
            if kind == "LabeledStatement":
                label = _identifier(node.get("label", {}).get("name"))
                self.diagnose(node, "label_approximation", "JavaScript label is emitted as a C# label", "labeled continue semantics may differ")
                return [pad + label + ":"] + self.stmt(node.get("body"), level, depth + 1)
            if kind == "DebuggerStatement":
                self.diagnose(node, "debugger_omitted", "debugger statement retained in diagnostic only", "no debugger instruction emitted")
                return [pad + "// Draft omission: debugger; " + self._comment(self.snippet(node))]
            if kind == "FunctionDeclaration":
                params, init = self.parameters(node.get("params", []), node)
                name = _target_identifier(node.get("id", {}), node.get("id", {}).get("name", "DraftFunction"))
                marker = self._embed_marker(node)
                lines = ([pad + marker.rstrip()] if marker else [])
                lines.append(pad + "dynamic " + name + "(" + ", ".join(params) + ")")
                lines.append(pad + "{")
                body = node.get("body", {})
                for child in body.get("body", []):
                    lines.extend(self.stmt(child, level + 1, depth + 1))
                lines.append(pad + "}")
                return lines
            if kind in ("ClassDeclaration", "WithStatement", "ImportDeclaration", "ExportNamedDeclaration", "ExportDefaultDeclaration", "ReturnStatement", "YieldExpression"):
                self.diagnose(node, "unsupported_statement", f"{kind} statement is retained locally and neighboring statements continue", "statement body omitted")
                return [pad + "// Draft omission " + kind + ": " + self._comment(self.snippet(node))]
            self.diagnose(node, "unsupported_statement", f"{kind!r} statement is retained locally and neighboring statements continue", "statement body omitted")
            return [pad + "// Draft omission " + str(kind) + ": " + self._comment(self.snippet(node))]
        except (KeyError, TypeError, ValueError, RecursionError) as error:
            self.diagnose(node, "statement_renderer_recovery", f"{kind!r} statement raised {type(error).__name__}; retained source comment and continued", "only this statement omitted")
            return [pad + "// Draft omission " + str(kind) + ": " + self._comment(self.snippet(node))]

    def render(self) -> dict[str, Any]:
        function = self.ast
        if function.get("type") in ("MethodDefinition", "PropertyDefinition"):
            function = function.get("value", {})
        if function.get("type") == "FunctionDeclaration":
            body = function.get("body", {})
            params_ast = function.get("params", [])
        elif function.get("type") in ("FunctionExpression", "ArrowFunctionExpression"):
            body = function.get("body", {})
            params_ast = function.get("params", [])
        else:
            # A parent may pass the method's BlockStatement directly.
            body = function if function.get("type") == "BlockStatement" else None
            params_ast = []
        if not isinstance(body, dict) or body.get("type") != "BlockStatement":
            self.diagnose(function, "method_body_missing", "AST input has no block body; source span retained as a diagnostic comment", "draft method has no emitted source body")
            body = {"type": "BlockStatement", "body": [], "start": function.get("start"), "end": function.get("end")}
        meta_params = self.method.get("parameters")
        if isinstance(meta_params, list) and not params_ast:
            params_ast = [{"type": "Identifier", "name": p.get("name")} if isinstance(p, dict) else {"type": "Identifier", "name": str(p)} for p in meta_params]
        params, setup = self.parameters(params_ast, function)
        original_names = set()
        for param in params_ast:
            if isinstance(param, dict):
                ident_node = param.get("left") if param.get("type") == "AssignmentPattern" else param.get("argument") if param.get("type") == "RestElement" else param
                if isinstance(ident_node, dict) and ident_node.get("type") == "Identifier":
                    original_names.add(_qualified_identifier(ident_node.get("_draftIdentifierTarget")) or _identifier(ident_node.get("name")))
        capture_params: list[str] = []
        captures = self.method.get("captureParameters", [])
        if isinstance(captures, list):
            for capture in captures:
                if not isinstance(capture, dict):
                    continue
                raw_target = capture.get("targetName")
                target_name = _identifier(raw_target) if isinstance(raw_target, str) and re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", raw_target) else None
                if target_name is None:
                    self.diagnose(function, "invalid_capture_parameter", "Capture parameter has no safe targetName and was omitted", "capture reference may remain unresolved")
                    continue
                if target_name in original_names or target_name in capture_params:
                    continue
                capture_params.append(target_name)
                params.append("dynamic " + target_name)
        name = _identifier(self.method.get("targetName") or self.method.get("name") or "DraftMethod")
        if self.class_name and name.lstrip("@").casefold() == self.class_name.lstrip("@").casefold():
            name += "_DraftMethod"
            self.diagnose(function, "method_name_class_collision", "Method name matches its containing class and was suffixed for C# syntax", "parent mapping must use the emitted targetName")
        async_flag = bool(function.get("async") or self.method.get("async"))
        if async_flag or self._contains_type(body, "AwaitExpression"):
            self.uses_tasks = True
            return_type = "System.Threading.Tasks.Task<dynamic>"
            modifier = "async "
            self.diagnose(function, "async_approximation", "Async method is emitted as Task<dynamic>", "JavaScript Promise rejection/order semantics are unverified")
        else:
            return_type = "dynamic"
            modifier = ""
        access = self.method.get("access", "public")
        if access not in ("public", "private", "protected", "internal"):
            access = "public"
        static = bool(self.method.get("static"))
        signature = f"{access} {'static ' if static else ''}{modifier}{return_type} {name}({', '.join(params)})"
        lines = ["    {"]
        for item in setup:
            lines.append("        " + item)
        if self._has_unmapped_this(body) and static:
            self.diagnose(body, "static_this_approximation", "Static source method references this; draft retains it as C# this and may not compile", "owner/static classification may be incomplete")
        emitted_body = []
        for stmt in body.get("body", []):
            emitted_body.extend(self.stmt(stmt, 2))
        meaningful = [line for line in emitted_body if line.strip() and not line.lstrip().startswith("//")]
        if not meaningful:
            self.diagnose(body, "empty_draft_body_blocked", "No executable statement could be rendered; emitted an explicit NotImplementedException", "prevents empty/default-success C# body")
            emitted_body.append("        throw new System.NotImplementedException(\"No source statement was renderable\");")
        lines.extend(emitted_body)
        lines.append("    }")
        usings = ["System", "System.Collections.Generic"]
        if self.uses_unity:
            usings.append("UnityEngine")
        if self.uses_tasks:
            usings.append("System.Threading.Tasks")
        if self.uses_linq:
            usings.append("System.Linq")
        return {"source": signature + "\n" + "\n".join(lines), "usings": sorted(set(usings)),
                "diagnostics": self.diagnostics, "approximateTypes": sorted(self.approx_types),
                "members": sorted(self.members), "emittedName": name.lstrip("@"),
                "embeddedFunctions": self.embedded_functions,
                "captureParameters": capture_params,
                "sourceSpan": self.method.get("sourceBytes"), "sourceExecuted": False,
                "draftOnly": True}

    def _contains_type(self, node: Any, kind: str) -> bool:
        if isinstance(node, dict):
            if node.get("type") == kind:
                return True
            return any(self._contains_type(value, kind) for key, value in node.items() if key not in ("start", "end"))
        if isinstance(node, list):
            return any(self._contains_type(value, kind) for value in node)
        return False

    def _has_unmapped_this(self, node: Any) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "ThisExpression":
                return _qualified_identifier(node.get("_draftStaticThisOwner")) is None
            mapping = node.get("_draftMember")
            if node.get("type") == "MemberExpression" and isinstance(mapping, dict) and mapping.get("receiver") == "static_owner":
                return any(self._has_unmapped_this(value) for key, value in node.items() if key not in ("object", "start", "end"))
            return any(self._has_unmapped_this(value) for key, value in node.items() if key not in ("start", "end"))
        if isinstance(node, list):
            return any(self._has_unmapped_this(value) for value in node)
        return False


def render_method(method: dict[str, Any], ast: dict[str, Any], source_bytes: bytes, *, class_name: str | None = None) -> dict[str, Any]:
    """Render one Acorn method AST to an approximate C# method draft.

    AST `start`/`end` offsets are UTF-8 byte offsets. `method` must contain a
    name and may include `sourceBytes`, `parameters`, `static`, `access`, and
    `async`. Unsupported nodes become escaped, local comments with diagnostics;
    later sibling statements are still rendered.
    """
    if not isinstance(method, dict) or not isinstance(ast, dict) or not isinstance(source_bytes, bytes):
        raise TypeError("method and AST must be objects and source_bytes must be bytes")
    if not isinstance(method.get("name"), str) or not method["name"]:
        raise ValueError("method.name is required")
    span = method.get("sourceBytes")
    if span is not None:
        if (not isinstance(span, dict) or type(span.get("start")) is not int or type(span.get("end")) is not int
                or not 0 <= span["start"] < span["end"] <= len(source_bytes)):
            raise ValueError("method.sourceBytes must be a valid UTF-8 byte span")
        expected = method.get("sourceSha256")
        if expected is not None and (not isinstance(expected, str) or hashlib.sha256(source_bytes[span["start"]:span["end"]]).hexdigest() != expected):
            raise ValueError("method.sourceSha256 does not match the supplied sourceBytes span")
    return _Renderer(method, ast, source_bytes, class_name).render()


def render_field(field: dict[str, Any], ast: dict[str, Any] | None, source_bytes: bytes, *, class_name: str | None = None) -> dict[str, Any]:
    """Render one source-bound static field initializer as a C# declaration.

    Field right-hand-side expressions use the same AST expression renderer as
    methods. Missing or unsupported initialization never becomes a default
    value: the candidate preserves an escaped source note and throws when the
    initializer is evaluated.
    """
    if not isinstance(field, dict) or not isinstance(source_bytes, bytes):
        raise TypeError("field must be an object and source_bytes must be bytes")
    if not isinstance(field.get("name"), str) or not field["name"]:
        raise ValueError("field.name is required")
    span = field.get("sourceBytes")
    if span is not None:
        if (not isinstance(span, dict) or type(span.get("start")) is not int or type(span.get("end")) is not int
                or not 0 <= span["start"] < span["end"] <= len(source_bytes)):
            raise ValueError("field.sourceBytes must be a valid UTF-8 byte span")
        expected = field.get("sourceSha256")
        if expected is not None and (not isinstance(expected, str) or hashlib.sha256(source_bytes[span["start"]:span["end"]]).hexdigest() != expected):
            raise ValueError("field.sourceSha256 does not match the supplied sourceBytes span")
    renderer = _Renderer(field, ast if isinstance(ast, dict) else {}, source_bytes, class_name)
    name = _identifier(field.get("targetName") or field["name"])
    if class_name and name.lstrip("@").casefold() == class_name.lstrip("@").casefold():
        name += "_DraftField"
        renderer.diagnose(ast, "field_name_class_collision", "Field name matches its containing class and was suffixed for C# syntax", "parent mapping must use the emittedName")
    if isinstance(ast, dict):
        initializer = renderer.expr(ast)
        if renderer._has_unmapped_this(ast):
            renderer.diagnose(ast, "field_initializer_this", "JavaScript this is retained in a C# field initializer; field initializers cannot use this", "receiver semantics remain unmodified and the draft may not compile")
    else:
        renderer.diagnose(field, "field_initializer_missing", "No initializer AST was supplied; original source is retained and access throws", "no default field value is inferred")
        span = field.get("sourceBytes", {})
        raw_fragment = ""
        if type(span.get("start")) is int and type(span.get("end")) is int and 0 <= span["start"] <= span["end"] <= len(source_bytes):
            raw_fragment = source_bytes[span["start"]:span["end"]].decode("utf-8", errors="replace")
        escaped = renderer._comment(raw_fragment)
        initializer = f"((System.Func<dynamic>)(() => {{ /* missing field AST: {escaped} */ throw new System.NotImplementedException(\"Field initializer AST unavailable\"); }}))()"
    access = field.get("access", "public")
    if access not in ("public", "private", "protected", "internal"):
        access = "public"
    static = bool(field.get("static", True))
    declaration = f"{access} {'static ' if static else ''}dynamic {name} = {initializer};"
    usings = ["System", "System.Collections.Generic"]
    if renderer.uses_unity:
        usings.append("UnityEngine")
    if renderer.uses_linq:
        usings.append("System.Linq")
    return {"source": declaration, "usings": sorted(set(usings)), "diagnostics": renderer.diagnostics,
            "approximateTypes": sorted(renderer.approx_types), "members": sorted(renderer.members),
            "embeddedFunctions": renderer.embedded_functions,
            "emittedName": name.lstrip("@"), "sourceSpan": field.get("sourceBytes"),
            "sourceExecuted": False, "draftOnly": True}
