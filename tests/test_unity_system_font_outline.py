from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = ROOT / "src/monkey/targets/UnitySystemFonts.cs"
RUNTIME_COMPONENT = ROOT / "src/monkey/targets/NativeStaticTextOutline.cs"


def normalized_outline(source_width, font_point_size, label_font_size, gradient_scale):
    return source_width * font_point_size / label_font_size / (gradient_scale - 1)


class UnitySystemFontOutlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = IMPLEMENTATION.read_text(encoding="utf-8")
        cls.runtime = RUNTIME_COMPONENT.read_text(encoding="utf-8")
        cls.method = cls.source.split("public static OutlineReadback ApplySourceOutline", 1)[1].split(
            "public static Readback Import(BindingSet bindingSet, string staticSdfGenerationReceiptPath", 1
        )[0]

    def test_outline_api_is_label_binding_driven_and_not_asset_or_name_special_cased(self):
        self.assertIn("ApplySourceOutline(TMP_Text label, BindingSet bindingSet", self.source)
        self.assertIn("sourceLabelId", self.method)
        self.assertIn("binding.nativeFallbackAssetPaths", self.method)
        self.assertIn("AddComponent<NativeStaticTextOutline>", self.method)
        self.assertIn("component.Configure(label, sourceOutlineWidth, sourceOutlineColor)", self.method)
        self.assertIn('serializedOutline.FindProperty("sourceOutlineWidth")', self.method)
        self.assertIn('serializedOutline.FindProperty("sourceOutlineColor")', self.method)
        self.assertIn('native.status == "not_visible_empty_text"', self.method)
        self.assertIn('native.status == "not_visible_empty_text"', self.method)
        self.assertNotIn("55960f08", self.method)
        self.assertNotIn("label_wait", self.method)

    def test_each_actual_glyph_font_uses_its_own_gradient_and_unclamped_source_width(self):
        primary = normalized_outline(4, 90, 36, 10)
        fallback = normalized_outline(4, 90, 36, 65)
        self.assertAlmostEqual(primary, 1.1111111111)
        self.assertAlmostEqual(fallback, 0.15625)
        self.assertIn("font.material.GetFloat(\"_GradientScale\")", self.runtime)
        self.assertIn("sourceOutlineWidth * pointSize / labelFontSize / (gradient - 1f)", self.runtime)
        self.assertNotIn("Mathf.Clamp", self.runtime)
        self.assertIn("TMP_MaterialManager.GetFallbackMaterial", self.runtime)
        self.assertIn("submesh.fontAsset != font", self.runtime)

    def test_face_dilate_comes_from_each_target_face_and_width_and_color_read_back(self):
        self.assertIn('font.material.GetFloat("_FaceDilate")', self.runtime)
        self.assertIn('material.SetFloat("_OutlineWidth", width)', self.runtime)
        self.assertIn('material.SetColor("_OutlineColor", sourceOutlineColor)', self.runtime)
        self.assertIn("normalizedOutlineWidth = width", self.runtime)
        self.assertIn("faceDilate = faceDilate", self.runtime)
        self.assertIn("[ExecuteAlways]", self.runtime)
        self.assertIn("OnPreRenderText += HandlePreRenderText", self.runtime)
        self.assertIn("target.ForceMeshUpdate(true, true)", self.runtime)
        self.assertIn('status = "not_visible_empty_text"', self.runtime)
        self.assertIn("target.ForceMeshUpdate(true, true)", self.runtime)
        self.assertIn('status = "not_visible_empty_text"', self.runtime)
        self.assertNotIn("UnityEditor", self.runtime)

    def test_generated_variants_are_per_font_cached_and_recreated_from_font_baselines(self):
        self.assertIn("readonly Dictionary<TMP_FontAsset, MaterialVariant> variants", self.runtime)
        self.assertIn("font.material", self.runtime)
        self.assertIn("ReleaseVariants()", self.runtime)
        self.assertIn("target.fontSharedMaterial = target.font.material", self.runtime)
        self.assertIn("HideFlags.HideAndDontSave", self.runtime)
        self.assertIn("public void Configure(TMP_Text text, float width, Color color)", self.runtime)
        self.assertNotIn("sourceLabelId", self.runtime)
        self.assertNotIn("sourceText", self.runtime)


if __name__ == "__main__":
    unittest.main()
