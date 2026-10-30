import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CREATOR = Path("/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/resources/3d/engine/cocos/2d/components/rich-text.ts")


class CreatorStaticSortRichTextTests(unittest.TestCase):
    def test_proxy_copies_typed_richtext_and_generated_segments(self):
        proxy = (ROOT / "src/monkey/targets/CreatorStaticSortQueueProxy.ts").read_text()
        presenter = (ROOT / "src/monkey/targets/CreatorStaticSortQueueProxyPresenter.ts").read_text()
        sdk = CREATOR.read_text()
        for field in ("string", "font", "useSystemFont", "fontFamily", "imageAtlas", "fontSize",
                      "maxWidth", "lineHeight", "horizontalAlign", "verticalAlign", "cacheMode", "handleTouchEvent"):
            self.assertIn(f"clone.{field} = rich.{field}", proxy)
            self.assertIn(f"{field}:", proxy)
        self.assertIn("clone.fontColor = new Color(rich.fontColor.r", proxy)
        self.assertIn("RICHTEXT_CHILD", sdk)
        self.assertIn("RICHTEXT_Image_CHILD", sdk)
        self.assertIn("hideFlags |= CCObjectFlags.DontSave", sdk)
        self.assertIn("labelSegment.node.layer = this.node.layer", sdk)
        self.assertIn("segment.node.layer = this.node.layer", sdk)
        self.assertIn("addRendererSortRank(proxyRenderer, row.sourceType, row.nativeSortingOrder)", proxy)
        self.assertIn("proxySortOrders", presenter)
        self.assertIn("clearGeneratedRichTextSorting", presenter)
        self.assertIn("sourceSegmentsHidden", proxy)
        self.assertIn("proxySegmentsCorrectLayer", proxy)
        self.assertIn("rendererFingerprint(source, marker.sourceType, runtimeSuppressionExpected)", proxy)

    def test_source_renderer_coverage_fails_closed_for_omitted_ui_renderers_and_richtext(self):
        proxy = (ROOT / "src/monkey/targets/CreatorStaticSortQueueProxy.ts").read_text()
        self.assertIn("assertSourceRendererCoverage(spec, nodes)", proxy)
        self.assertIn("CREATOR_PROXY_UNCOVERED_SOURCE_UIRENDERER", proxy)
        self.assertIn("CREATOR_PROXY_UNCOVERED_SOURCE_RICHTEXT", proxy)
        self.assertIn("CREATOR_PROXY_MASK_BACKING_MUST_NOT_BE_A_DRAW_ROW", proxy)
        self.assertIn("verifyRichTextSourceProof", proxy)

    def test_initialized_camera_proof_uses_the_owned_source_scene_and_canvas_camera(self):
        proxy = (ROOT / "src/monkey/targets/CreatorStaticSortQueueProxy.ts").read_text()
        self.assertIn("const scene = sourceRootNode?.scene", proxy)
        self.assertIn("const proxyScene = proxyRoot.scene", proxy)
        self.assertIn("scene === proxyScene", proxy)
        self.assertIn("const canvasCamera = canvas?.cameraComponent", proxy)
        self.assertIn("nodeIsWithin(sourceRootNode || null, canvas.node)", proxy)
        self.assertIn("cameras.includes(canvasCamera)", proxy)
        self.assertNotIn("director.getScene()", proxy)


if __name__ == "__main__":
    unittest.main()
