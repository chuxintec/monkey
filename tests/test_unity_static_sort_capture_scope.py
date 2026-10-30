import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "src/monkey/targets/UnityStaticSortQueueProxy.cs"


class UnityStaticSortCaptureScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def block(self, start, end):
        a = self.source.index(start)
        b = self.source.index(end, a)
        return self.source[a:b]

    def test_nested_presenters_restore_source_cull_before_hiding_proxy_roots(self):
        scope = self.block("sealed class NestedProxyCaptureScope", "static void EnsureSourceGraphicMeshReady")
        self.assertLess(scope.index("presenters[i].enabled = false"), scope.index("roots[i].SetActive(false)"))
        self.assertIn("if (presenters[i] != null) presenters[i].enabled = presenterEnabledBefore[i];", scope)
        self.assertIn("if (roots[i] != null) roots[i].SetActive(rootActiveBefore[i]);", scope)
        self.assertIn("!IsGeneratedSortProxyRoot(roots[i].transform)", scope)

    def test_capture_prepares_typed_sources_and_keeps_spine_and_tmp_child_mesh_owners(self):
        prepare = self.block("static void EnsureSourceGraphicMeshReady", "static void InitializeSourceSpineStaticPose")
        self.assertLess(prepare.index("IsSpineCanvasSubmesh"), prepare.index("graphic.SetAllDirty()"))
        self.assertIn("IsGeneratedTextSubmesh(graphic.gameObject)", prepare)
        self.assertIn("tmp.ForceMeshUpdate(true, false)", prepare)
        self.assertIn("InitializeSourceSpineStaticPose(sourceRoot)", self.source)

    def test_capture_scope_wraps_creation_and_commits_after_outer_suppression(self):
        wrapper = self.block("public static ProxyQueueReadback CreateStaticSortQueueProxy(",
                             "static ProxyQueueReadback CreateStaticSortQueueProxyCore(")
        core = self.block("static ProxyQueueReadback CreateStaticSortQueueProxyCore(",
                          "public static ProxyQueueReadback ReadStaticSortQueueProxy(")
        self.assertIn("using (var capture = new NestedProxyCaptureScope", wrapper)
        self.assertIn("PrepareSourceGeometryForCapture(spec, sourceNodes, sourceRoot)", core)
        self.assertLess(core.index("presenter.InitializePresentation()"), core.index("nestedCapture.Commit()"))

    def test_readback_keeps_failed_rows_and_continues_across_siblings(self):
        read = self.block("static ProxyQueueReadback ReadProxy(", "\n    }\n\n}")
        self.assertIn("if (empty != null) emptyGraphics.Add(empty);", read)
        self.assertIn("structuralDiagnostics.Add(\"STATIC_SORT_PROXY_EMPTY_RENDERER_READBACK_INVALID", read)
        self.assertIn("foreach (Transform child in node) if (!Visit(child)) childrenOK = false;", read)
        self.assertIn("structuralDiagnostics = structuralDiagnostics.ToArray()", read)
        self.assertIn("STATIC_SORT_PROXY_GRAPHIC_READBACK_INVALID", read)
        self.assertIn("STATIC_SORT_PROXY_MASK_READBACK_INVALID", read)

    def test_tmp_capture_and_readback_use_persistent_owner_slot_bindings(self):
        prepare = self.block("static Dictionary<string, OwnerFontStyleDescriptor> PrepareSourceGeometryForCapture",
                             "static string OwnerFontMaterialPath")
        create = self.block("static NativeStaticSortQueueProxyGraphic CreateProxyGraphic(",
                            "public static ProxyQueueReadback CreateStaticSortQueueProxy(")
        core = self.block("static ProxyQueueReadback CreateStaticSortQueueProxyCore(",
                          "public static ProxyQueueReadback ReadStaticSortQueueProxy(")
        read = self.block("static ProxyQueueReadback ReadProxy(", "\n    }\n\n}")
        self.assertIn("UnityStaticSortTextSource.PrepareSource(textOwner", prepare)
        self.assertIn("CaptureOwnerFontMaterial(textOwner, row.sourceComponentId", prepare)
        self.assertLess(prepare.index("PrepareSource(textOwner, row.sourceComponentId"),
                        prepare.index("CaptureOwnerFontMaterial(textOwner, row.sourceComponentId"))
        self.assertGreater(prepare.rindex("PrepareSource(textOwner, row.sourceComponentId"),
                           prepare.index("CaptureOwnerFontMaterial(textOwner, row.sourceComponentId"))
        self.assertIn("CaptureAndRebindTextSlots(spec, row, textOwner, ownerStyle, out var textSlotEnumeration)", core)
        self.assertIn("RebindCapturedSlot(captureProofs[slot], owner, current.sourceGraphic", self.source)
        self.assertIn("GetCurrentSlots(owner, row.sourceComponentId", self.source)
        self.assertIn("CaptureFallbackMaterial(live, materialPath", self.source)
        self.assertLess(self.source.index("CaptureFallbackMaterial(live, materialPath"),
                        self.source.index("PrepareSource(owner, row.sourceComponentId", self.source.index("CaptureFallbackMaterial(live, materialPath")))
        self.assertLess(core.index("CaptureAndRebindTextSlots(spec, row, textOwner, ownerStyle, out var textSlotEnumeration)"),
                        core.index("CreateProxyGraphic(sourceGraphic"))
        self.assertIn("UnityStaticSortTextSource.Attach(proxyObject, textBinding, mesh, meshSha)", create)
        self.assertIn("UnityStaticSortTextSource.ReadPersistent", read)
        self.assertIn("UnityStaticSortTextSource.ReadInitialized", read)
        self.assertIn("textSources = textSourceReadbacks.ToArray()", read)

    def test_optional_mask_proof_strings_canonicalize_null_without_dropping_checks(self):
        for source_name in ("maskSpec", "sourceMask"):
            for field in ("sourceMaterialId", "resolvedSourceMaterialId", "sourceEffectId",
                          "sourceEffectName", "sourceEffectDocumentSha256"):
                self.assertIn(f"{field} = {source_name}.{field} ?? String.Empty", self.source)
        self.assertIn("maskIdentity.sourceFieldsJson == sourceMask.sourceFieldsJson", self.source)
        self.assertIn("maskIdentity.sourceAlphaThreshold == sourceMask.alphaThreshold", self.source)

    def test_empty_renderer_optional_fields_canonicalize_null_but_keep_raw_graphics_hash(self):
        empty = self.block("static ProxyEmptyRendererReadback ReadEmptyRenderer(", "static NativeStaticSortQueueProxyGraphic CreateProxyGraphic(")
        carrier = self.block("static bool TryCreateEmptyRendererCarrier(", "static bool GraphicsMaterialGuidsMatch(")
        self.assertIn("spec.sourceFieldsJson ?? String.Empty", carrier)
        self.assertIn("spec.sourceFieldsSha256 ?? String.Empty", carrier)
        self.assertIn("spec.sourceDrawingCommands ?? String.Empty", carrier)
        self.assertIn("String.Equals(marker.sourceFieldsJson ?? String.Empty, expectedSourceFieldsJson", empty)
        self.assertIn("HashText(expectedSourceFieldsJson) == expectedSourceFieldsSha256", empty)


if __name__ == "__main__":
    unittest.main()
