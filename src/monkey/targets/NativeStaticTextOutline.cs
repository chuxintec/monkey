using System;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

// Persistent, source-declared TMP outline state for static native previews.
// The component owns only presentation values; it never executes source behavior.
[ExecuteAlways]
[DisallowMultipleComponent]
public sealed class NativeStaticTextOutline : MonoBehaviour
{
    [Serializable]
    public sealed class FaceReadback
    {
        [NonSerialized] public TMP_FontAsset fontAsset;
        public string fontName;
        public string materialName;
        public int[] assignedUnicode;
        public float pointSize;
        public float gradientScale;
        public float faceDilate;
        public float sourceOutlineWidth;
        public float normalizedOutlineWidth;
        public Color outlineColor;
        public bool materialValuesVerified;
    }

    [Serializable]
    public sealed class Readback
    {
        public string status;
        public float sourceOutlineWidth;
        public Color sourceOutlineColor;
        public FaceReadback[] faces;
        public string[] diagnostics;
    }

    [SerializeField] TMP_Text target;
    [SerializeField, Min(0f)] float sourceOutlineWidth;
    [SerializeField] Color sourceOutlineColor = Color.black;

    readonly Dictionary<TMP_FontAsset, MaterialVariant> variants = new Dictionary<TMP_FontAsset, MaterialVariant>();
    readonly Dictionary<TMP_SubMeshUI, SubmeshBaseline> submeshBaselines = new Dictionary<TMP_SubMeshUI, SubmeshBaseline>();
    TMP_Text subscribedTarget;
    bool applying;
    Readback lastReadback = new Readback { status = "not_run" };

    sealed class MaterialVariant
    {
        public TMP_FontAsset font;
        public Material material;
    }

    sealed class SubmeshBaseline
    {
        public TMP_SubMeshUI submesh;
        public Material sourceMaterial;
        public Material fallbackMaterial;
    }

    public TMP_Text Target { get { return target; } }
    public float SourceOutlineWidth { get { return sourceOutlineWidth; } }
    public Color SourceOutlineColor { get { return sourceOutlineColor; } }
    public Readback LastReadback { get { return lastReadback; } }

    public void Configure(TMP_Text text, float width, Color color)
    {
        if (text == null) throw new ArgumentNullException(nameof(text));
        if (float.IsNaN(width) || float.IsInfinity(width) || width < 0f)
            throw new ArgumentOutOfRangeException(nameof(width));
        target = text;
        sourceOutlineWidth = width;
        sourceOutlineColor = color;
        BindTarget();
        RefreshNow();
    }

    void OnEnable()
    {
        if (target == null) target = GetComponent<TMP_Text>();
        BindTarget();
        if (target != null) RefreshNow();
    }

    void OnDisable()
    {
        UnbindTarget();
        ReleaseVariants();
    }

    void OnDestroy()
    {
        UnbindTarget();
        ReleaseVariants();
    }

    void OnValidate()
    {
        if (target == null) target = GetComponent<TMP_Text>();
        if (isActiveAndEnabled && target != null)
        {
            BindTarget();
            RefreshNow();
        }
    }

    void BindTarget()
    {
        if (subscribedTarget == target) return;
        UnbindTarget();
        if (target == null) return;
        subscribedTarget = target;
        subscribedTarget.OnPreRenderText += HandlePreRenderText;
    }

    void UnbindTarget()
    {
        if (subscribedTarget != null)
            subscribedTarget.OnPreRenderText -= HandlePreRenderText;
        subscribedTarget = null;
    }

    void HandlePreRenderText(TMP_TextInfo textInfo)
    {
        Apply(textInfo);
    }

    public Readback RefreshNow()
    {
        if (target == null)
        {
            lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_TARGET_MISSING");
            return lastReadback;
        }
        BindTarget();
        target.ForceMeshUpdate(true, true);
        // The callback normally runs during ForceMeshUpdate. Applying once more
        // guarantees a deterministic readback even when TMP skips unchanged text.
        Apply(target.textInfo);
        return lastReadback;
    }

    void Apply(TMP_TextInfo textInfo)
    {
        if (applying) return;
        applying = true;
        try
        {
            if (target == null || target.font == null)
            {
                lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_TEXT_UNAVAILABLE");
                return;
            }
            if (string.IsNullOrEmpty(target.text))
            {
                lastReadback = new Readback {
                    status = "not_visible_empty_text",
                    sourceOutlineWidth = sourceOutlineWidth,
                    sourceOutlineColor = sourceOutlineColor,
                    faces = Array.Empty<FaceReadback>(),
                    diagnostics = new[] { "Empty source text has no glyph geometry; serialized outline inputs were retained." },
                };
                return;
            }
            if (textInfo == null || textInfo.characterCount <= 0)
            {
                lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_TEXT_INFO_MISSING");
                return;
            }
            float fontSize = target.fontSize;
            if (!Finite(fontSize) || fontSize <= 0f || !Finite(sourceOutlineWidth) || sourceOutlineWidth < 0f)
            {
                lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_METRICS_INVALID");
                return;
            }

            var assigned = new Dictionary<TMP_FontAsset, SortedSet<int>>();
            for (int i = 0; i < textInfo.characterCount; i++)
            {
                var character = textInfo.characterInfo[i];
                int unicode = character.textElement == null
                    ? char.ConvertToUtf32(character.character.ToString(), 0)
                    : checked((int)character.textElement.unicode);
                if (unicode == '\n' || unicode == '\r' || unicode == '\t') continue;
                var font = character.fontAsset;
                if (font == null)
                {
                    lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_GLYPH_FONT_MISSING_U+" + unicode.ToString("X4"));
                    return;
                }
                if (!assigned.TryGetValue(font, out var scalars))
                    assigned.Add(font, scalars = new SortedSet<int>());
                scalars.Add(unicode);
            }
            if (assigned.Count == 0)
            {
                lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_NO_RENDERED_GLYPHS");
                return;
            }

            // Build the primary material first. TMP's fallback material manager uses
            // this as the source style while taking atlas and gradient from each face.
            var primary = GetVariant(target.font);
            bool requiresPaddingUpdate = ConfigureMaterial(primary, target.font, fontSize);
            if (target.fontSharedMaterial != primary)
            {
                target.fontSharedMaterial = primary;
                requiresPaddingUpdate = true;
            }

            var rows = new List<FaceReadback>();
            foreach (var entry in assigned)
            {
                var font = entry.Key;
                if (font == null)
                {
                    lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_FONT_LOOKUP_FAILED");
                    return;
                }
                Material material;
                if (font == target.font)
                {
                    material = primary;
                }
                else
                {
                    var fallbackTemplate = TMP_MaterialManager.GetFallbackMaterial(primary, font.material);
                    if (fallbackTemplate == null)
                    {
                        lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_FALLBACK_MATERIAL_MISSING: " + font.name);
                        return;
                    }
                    material = GetVariant(font, fallbackTemplate);
                    requiresPaddingUpdate |= ConfigureMaterial(material, font, fontSize);
                    var submeshes = target.GetComponentsInChildren<TMP_SubMeshUI>(true);
                    bool found = false;
                    foreach (var submesh in submeshes)
                    {
                        if (submesh == null || submesh.fontAsset != font) continue;
                        if (!submeshBaselines.ContainsKey(submesh))
                            submeshBaselines.Add(submesh, new SubmeshBaseline {
                                submesh = submesh,
                                sourceMaterial = submesh.fallbackSourceMaterial,
                                fallbackMaterial = submesh.fallbackMaterial,
                            });
                        if (submesh.fallbackSourceMaterial != primary || submesh.fallbackMaterial != material)
                        {
                            submesh.fallbackSourceMaterial = primary;
                            submesh.fallbackMaterial = material;
                            requiresPaddingUpdate = true;
                        }
                        if (submesh.fallbackMaterial != material)
                        {
                            lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_FALLBACK_MATERIAL_READBACK_MISMATCH: " + font.name);
                            return;
                        }
                        found = true;
                    }
                    if (!found)
                    {
                        lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_FALLBACK_SUBMESH_MISSING: " + font.name);
                        return;
                    }
                }
                rows.Add(ReadFace(font, material, entry.Value));
            }
            if (requiresPaddingUpdate) target.UpdateMeshPadding();
            lastReadback = new Readback {
                status = rows.TrueForAll(row => row.materialValuesVerified)
                    ? "material_values_applied_and_read_back" : "partial",
                sourceOutlineWidth = sourceOutlineWidth,
                sourceOutlineColor = sourceOutlineColor,
                faces = rows.ToArray(),
                diagnostics = Array.Empty<string>(),
            };
        }
        catch (Exception exception)
        {
            lastReadback = Failure("NATIVE_STATIC_TEXT_OUTLINE_APPLY_FAILED: " + exception.GetType().Name);
        }
        finally
        {
            applying = false;
        }
    }

    Material GetVariant(TMP_FontAsset font, Material fallbackTemplate = null)
    {
        if (variants.TryGetValue(font, out var existing) && existing.font == font && existing.material != null)
            return existing.material;
        var source = fallbackTemplate != null ? fallbackTemplate : font.material;
        if (source == null) throw new InvalidOperationException("NATIVE_STATIC_TEXT_OUTLINE_FONT_MATERIAL_MISSING");
        var material = new Material(source) { name = source.name + " [native-static-outline]", hideFlags = HideFlags.HideAndDontSave };
        variants[font] = new MaterialVariant { font = font, material = material };
        return material;
    }

    bool ConfigureMaterial(Material material, TMP_FontAsset font, float labelFontSize)
    {
        if (font == null || font.material == null || material == null
            || !material.HasProperty("_GradientScale") || !material.HasProperty("_OutlineWidth")
            || !material.HasProperty("_OutlineColor"))
            throw new InvalidOperationException("NATIVE_STATIC_TEXT_OUTLINE_SHADER_PROPERTIES_MISSING");
        float gradient = font.material.GetFloat("_GradientScale");
        float pointSize = font.faceInfo.pointSize;
        if (!Finite(gradient) || gradient <= 1f || !Finite(pointSize) || pointSize <= 0f)
            throw new InvalidOperationException("NATIVE_STATIC_TEXT_OUTLINE_FONT_METRICS_INVALID");
        float width = sourceOutlineWidth * pointSize / labelFontSize / (gradient - 1f);
        float faceDilate = font.material.HasProperty("_FaceDilate") ? font.material.GetFloat("_FaceDilate") : 0f;
        bool changed = !Mathf.Approximately(material.GetFloat("_OutlineWidth"), width)
            || !Mathf.Approximately(material.GetFloat("_GradientScale"), gradient)
            || material.GetColor("_OutlineColor") != sourceOutlineColor
            || (material.HasProperty("_FaceDilate") && !Mathf.Approximately(material.GetFloat("_FaceDilate"), faceDilate));
        if (!Mathf.Approximately(material.GetFloat("_OutlineWidth"), width)) material.SetFloat("_OutlineWidth", width);
        if (material.GetColor("_OutlineColor") != sourceOutlineColor) material.SetColor("_OutlineColor", sourceOutlineColor);
        if (material.HasProperty("_FaceDilate") && !Mathf.Approximately(material.GetFloat("_FaceDilate"), faceDilate))
            material.SetFloat("_FaceDilate", faceDilate);
        // A fallback variant must keep its own atlas/range even after the manager
        // copies primary style properties onto it.
        if (!Mathf.Approximately(material.GetFloat("_GradientScale"), gradient)) material.SetFloat("_GradientScale", gradient);
        if (!Mathf.Approximately(material.GetFloat("_OutlineWidth"), width)
            || !Mathf.Approximately(material.GetFloat("_GradientScale"), gradient)
            || material.GetColor("_OutlineColor") != sourceOutlineColor
            || (material.HasProperty("_FaceDilate") && !Mathf.Approximately(material.GetFloat("_FaceDilate"), faceDilate)))
            throw new InvalidOperationException("NATIVE_STATIC_TEXT_OUTLINE_MATERIAL_READBACK_MISMATCH");
        return changed;
    }

    FaceReadback ReadFace(TMP_FontAsset font, Material material, SortedSet<int> assignedUnicode)
    {
        float gradient = font.material.GetFloat("_GradientScale");
        float pointSize = font.faceInfo.pointSize;
        float faceDilate = font.material.HasProperty("_FaceDilate") ? font.material.GetFloat("_FaceDilate") : 0f;
        float width = sourceOutlineWidth * pointSize / target.fontSize / (gradient - 1f);
        return new FaceReadback {
            fontAsset = font,
            fontName = font.name,
            materialName = material.name,
            assignedUnicode = new List<int>(assignedUnicode).ToArray(),
            pointSize = pointSize,
            gradientScale = gradient,
            faceDilate = faceDilate,
            sourceOutlineWidth = sourceOutlineWidth,
            normalizedOutlineWidth = width,
            outlineColor = sourceOutlineColor,
            materialValuesVerified = Mathf.Approximately(material.GetFloat("_GradientScale"), gradient)
                && Mathf.Approximately(material.GetFloat("_OutlineWidth"), width)
                && material.GetColor("_OutlineColor") == sourceOutlineColor
                && (!material.HasProperty("_FaceDilate")
                    || Mathf.Approximately(material.GetFloat("_FaceDilate"), faceDilate)),
        };
    }

    Readback Failure(string diagnostic)
    {
        return new Readback {
            status = "failed",
            sourceOutlineWidth = sourceOutlineWidth,
            sourceOutlineColor = sourceOutlineColor,
            faces = Array.Empty<FaceReadback>(),
            diagnostics = new[] { diagnostic },
        };
    }

    void ReleaseVariants()
    {
        foreach (var baseline in submeshBaselines.Values)
            if (baseline.submesh != null && IsOwnedMaterial(baseline.submesh.fallbackMaterial))
            {
                baseline.submesh.fallbackSourceMaterial = baseline.sourceMaterial;
                baseline.submesh.fallbackMaterial = baseline.fallbackMaterial;
            }
        submeshBaselines.Clear();
        if (target != null && target.font != null && IsOwnedMaterial(target.fontSharedMaterial))
            target.fontSharedMaterial = target.font.material;
        foreach (var row in variants.Values)
            if (row.material != null)
            {
                if (Application.isPlaying) Destroy(row.material);
                else DestroyImmediate(row.material);
            }
        variants.Clear();
    }

    bool IsOwnedMaterial(Material material)
    {
        if (material == null) return false;
        foreach (var row in variants.Values)
            if (row.material == material) return true;
        return false;
    }

    static bool Finite(float value) { return !float.IsNaN(value) && !float.IsInfinity(value); }
}
