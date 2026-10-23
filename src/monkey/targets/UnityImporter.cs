// Conversion-only native Editor adapter. No source graph is loaded by the Player.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class MonkeyImporter
{
    [Serializable] public class Plan {
        public float[] designSize; public float pixelsPerUnit;
        public TextureSpec[] textures; public AssetSpec[] assets; public BitmapSpec[] bitmapFonts; public int sourceDiagnosticCount;
        public NodeSpec[] nodes; public ComponentSpec[] components; public MotionSpec[] animations; public bool galleryOnly; public SourcePrefabSpec[] sourcePrefabs;
    }
    [Serializable] public class SourcePrefabSpec { public string sourceId,root,path; public string[] nodes; public int nodeCount; }
    [Serializable] public class SourcePrefabResult { public string sourceId,path,guid; public int nodeCount,missingScripts; }
    [Serializable] public class MotionKey { public float time,value; public string interpolation; }
    [Serializable] public class MotionProbe { public float time,value; }
    [Serializable] public class MotionTrack { public string node,path,nativeType,nativeProperty; public MotionKey[] keys; public MotionProbe[] probes; }
    [Serializable] public class MotionSpec { public string id,name,root,path,wrap; public float duration,sample; public bool convertible; public MotionTrack[] tracks; }
    [Serializable] public class MotionTrackResult { public string path,property,nativeType; public float[] times,values,probeTimes,probeValues; public string[] interpolations; }
    [Serializable] public class MotionResult { public string id,path,guid,wrap; public float duration; public int eventCount,curveCount; public MotionTrackResult[] tracks; }
    [Serializable] public class TextureSpec {
        public string id, path; public float[] border, size, originalSize, offset;
    }
    [Serializable] public class AssetSpec { public string id, kind, path; }
    [Serializable] public class NodeSpec {
        public string sourceId, name, parent; public string[] children, components;
        public float[] position, rotation, scale, size, anchor, color;
        public float opacity; public bool active;
    }
    [Serializable] public class ComponentSpec {
        public string sourceId, type, node, spriteFrame, font, text;
        public int mode, sizeMode, horizontalAlign, verticalAlign, overflow; public float fontSize,lineHeight;
        public bool enabled, convertible, trim, wrap, bold, italic; public float spacing; public BitmapProbe bitmapProbe;
        public string target,content,nativeId; public int flags,maskType,layoutType,resize,horizontalDirection,verticalDirection,startAxis,transition;
        public bool inverted,horizontal,vertical,interactable; public float zoomScale,duration,width;
        public float[] margins,spacingXY,padding,effectiveCellSize,outlineColor;
    }
    [Serializable] public class BitmapProbe { public float advance,inkRight; }
    [Serializable] public class BitmapSpec {
        public string id, path, fontPath; public float pointSize, lineHeight, ascent, descent;
        public int[] atlasSize; public GlyphSpec[] glyphs; public KerningSpec[] kernings;
    }
    [Serializable] public class GlyphSpec { public uint unicode, index; public int[] rect; public float[] metrics; }
    [Serializable] public class KerningSpec { public uint first, second; public float advance; }
    [Serializable] public class FontResult { public string id, guid; public int glyphCount, characterCount; public float pointSize, lineHeight; }
    [Serializable] public class LabelResult { public string sourceId, text, fontGuid; public float fontSize; public int characterCount; public bool allCharactersPresent; public GlyphBounds[] glyphBounds; }
    [Serializable] public class GlyphBounds { public uint unicode; public float left,top,width,height; }
    [Serializable] public class Readback {
        public string status, unityVersion, prefabGuid, sceneGuid;
        public int spriteCount, nodeCount, missingScripts; public bool editableRoundtrip; public string previewPath,previewSha256,previewError,colorSpace;
        public MotionResult[] animations; public string[] diagnostics; public NodeResult[] nodes; public SpriteResult[] sprites; public FileResult[] nativeFiles; public FontResult[] fonts; public LabelResult[] labels; public ViewReference[] viewReferences; public JsonResult[] jsonAssets; public SourcePrefabResult[] sourcePrefabs;
    }
    [Serializable] public class JsonResult { public string id,guid,textSha256; }
    [Serializable] public class ViewReference { public string sourceId,field; public int index; public long prefabFileId; public bool bound; }
    [Serializable] public class FileResult { public string path, sha256; }
    [Serializable] public class NodeResult {
        public string sourceId, hierarchy; public float[] size, pivot, position;
        public bool active; public string[] componentTypes;
    }
    [Serializable] public class SpriteResult {
        public string id, guid; public float[] size, border;
        public long fileId;
    }
    const string PrefabPath = "Assets/Generated/Views/Candidate.prefab";
    const string ScenePath = "Assets/Generated/Scenes/Candidate.unity";
    const string BootstrapPath = "Assets/Generated/Scenes/ImportBootstrap.unity";

    [MenuItem("Tools/Monkey/Import Candidate")]
    public static void ImportCandidate() { Run(); }
    public static void ImportBatch() { Run(); }

    static void Run()
    {
        if (Application.unityVersion != "6000.6.2f1")
            throw new InvalidOperationException("Candidate requires Unity 6000.6.2f1; no automatic version migration");
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Editor must be idle");
        if (File.Exists(PrefabPath) || File.Exists(ScenePath) || File.Exists(BootstrapPath))
            throw new InvalidOperationException("Create-only import: Prefab/Scene already exists. Use a new candidate.");
        if (SceneManager.GetActiveScene().isDirty)
            throw new InvalidOperationException("Active scene has unsaved work; import refused");
        var plan = JsonUtility.FromJson<Plan>(File.ReadAllText("Assets/Monkey/Editor/import-plan.json"));
        var diagnostics = new List<string>();
        foreach(var directory in new[]{Path.GetDirectoryName(PrefabPath),Path.GetDirectoryName(ScenePath),"Assets/Generated/Art","Assets/Generated/Controllers","Analysis"})
            Directory.CreateDirectory(directory);
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        if (plan.sourceDiagnosticCount > 0) diagnostics.Add("SOURCE_GAPS: " + plan.sourceDiagnosticCount);
        var spriteMap = new Dictionary<string, Sprite>();
        foreach (var item in plan.textures)
        {
            AssetDatabase.ImportAsset(item.path,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);
            var importer = AssetImporter.GetAtPath(item.path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException("Missing texture importer: " + item.path);
            importer.textureType = TextureImporterType.Sprite;
            importer.textureShape = TextureImporterShape.Texture2D;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = plan.pixelsPerUnit;
            importer.spritePivot = new Vector2(.5f,.5f);
            importer.spriteBorder = new Vector4(item.border[0],item.border[1],item.border[2],item.border[3]);
            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteMeshType = SpriteMeshType.FullRect;
            importer.SetTextureSettings(settings);
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = 16384;
            // Color space / alpha origin remains unknown in Analysis, never asserted as matched.
            importer.SaveAndReimport();
            AssetDatabase.ImportAsset(item.path,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);
            var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(item.path);
            if (sprite == null) throw new InvalidOperationException("Sprite import failed: " + item.path);
            spriteMap.Add(item.id,sprite);
        }
        if (plan.bitmapFonts.Length > 0 || plan.assets.Any(a=>a.path.EndsWith(".ttf",StringComparison.OrdinalIgnoreCase))) {
            if (Shader.Find("TextMeshPro/Bitmap Custom Atlas") == null || Shader.Find("TextMeshPro/Distance Field") == null)
                TMPro.TMP_PackageResourceImporter.ImportResources(true,false,false);
        }
        var fonts = new Dictionary<string, TMPro.TMP_FontAsset>();
        foreach (var item in plan.assets.Where(a => a.path.EndsWith(".ttf", StringComparison.OrdinalIgnoreCase)))
        {
            var source = AssetDatabase.LoadAssetAtPath<Font>(item.path);
            if (source == null) { diagnostics.Add("FONT_IMPORT_FAILED: " + item.id); continue; }
            if (Shader.Find("TextMeshPro/Distance Field") == null) {
                diagnostics.Add("TMP_SHADER_RESOURCES_MISSING: " + item.id); continue;
            }
            var font = TMPro.TMP_FontAsset.CreateFontAsset(source,90,16,UnityEngine.TextCore.LowLevel.GlyphRenderMode.SDFAA,1024,1024,TMPro.AtlasPopulationMode.Dynamic,false);
            if (font == null) { diagnostics.Add("TMP_FONT_CREATION_FAILED: " + item.id); continue; }
            var needed = string.Concat(plan.components.Where(c=>c.type=="cc.Label" && c.convertible && c.font==item.id).Select(c=>c.text));
            if (!font.TryAddCharacters(needed,out string missing)) {diagnostics.Add("TTF_GLYPHS_MISSING: " + missing);UnityEngine.Object.DestroyImmediate(font);continue;}
            font.atlasPopulationMode=TMPro.AtlasPopulationMode.Static;
            font.fallbackFontAssetTable=new List<TMPro.TMP_FontAsset>();
            var path = item.path.Substring(0,item.path.Length-4) + ".asset";
            if (File.Exists(path)) throw new InvalidOperationException("Font target exists: " + path);
            AssetDatabase.CreateAsset(font,path);
            if (font.material != null) AssetDatabase.AddObjectToAsset(font.material,font);
            foreach (var atlas in font.atlasTextures)
                if (atlas != null) AssetDatabase.AddObjectToAsset(atlas,font);
            EditorUtility.SetDirty(font);
            AssetDatabase.SaveAssetIfDirty(font);
            fonts[item.id] = font;
        }
        foreach (var spec in plan.bitmapFonts) {
            var atlasImporter = AssetImporter.GetAtPath(spec.path) as TextureImporter;
            if (atlasImporter == null) throw new InvalidOperationException("Bitmap atlas missing: " + spec.id);
            atlasImporter.textureType = TextureImporterType.Default;
            atlasImporter.mipmapEnabled = false; atlasImporter.npotScale = TextureImporterNPOTScale.None;
            atlasImporter.textureCompression = TextureImporterCompression.Uncompressed; atlasImporter.maxTextureSize = 16384;
            atlasImporter.SaveAndReimport();
            var atlas = AssetDatabase.LoadAssetAtPath<Texture2D>(spec.path);
            var shader = Shader.Find("TextMeshPro/Bitmap Custom Atlas");
            if (shader == null) throw new InvalidOperationException("Native TMP bitmap shader unavailable after resource import");
            var font = ScriptableObject.CreateInstance<TMPro.TMP_FontAsset>();
            font.name = "SourceBitmapFont";
            font.faceInfo = new UnityEngine.TextCore.FaceInfo {
                familyName="SourceBitmapFont",styleName="Original",pointSize=(int)spec.pointSize,scale=1,
                lineHeight=spec.lineHeight,ascentLine=spec.ascent,descentLine=spec.descent,
                capLine=spec.ascent,meanLine=spec.ascent*.5f,baseline=0
            };
            font.atlasPopulationMode = TMPro.AtlasPopulationMode.Static;
            font.atlasTextures = new[] { atlas };
            font.fallbackFontAssetTable = new List<TMPro.TMP_FontAsset>();

            var serialized = new SerializedObject(font);
            serialized.FindProperty("m_Version").stringValue = "1.1.0";
            serialized.FindProperty("m_AtlasWidth").intValue = spec.atlasSize[0];
            serialized.FindProperty("m_AtlasHeight").intValue = spec.atlasSize[1];
            serialized.FindProperty("m_AtlasPadding").intValue = 0;
            serialized.FindProperty("m_AtlasRenderMode").intValue=(int)UnityEngine.TextCore.LowLevel.GlyphRenderMode.RASTER;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            foreach (var g in spec.glyphs) {
                var glyph = new UnityEngine.TextCore.Glyph(g.index,
                    new UnityEngine.TextCore.GlyphMetrics(g.metrics[0],g.metrics[1],g.metrics[2],g.metrics[3],g.metrics[4]),
                    new UnityEngine.TextCore.GlyphRect(g.rect[0],g.rect[1],g.rect[2],g.rect[3]),1,0);
                font.glyphTable.Add(glyph);font.characterTable.Add(new TMPro.TMP_Character(g.unicode,font,glyph));
            }
            font.fontFeatureTable.glyphPairAdjustmentRecords = new List<UnityEngine.TextCore.LowLevel.GlyphPairAdjustmentRecord>();
            foreach (var k in spec.kernings) {
                font.fontFeatureTable.glyphPairAdjustmentRecords.Add(new UnityEngine.TextCore.LowLevel.GlyphPairAdjustmentRecord {
                    firstAdjustmentRecord=new UnityEngine.TextCore.LowLevel.GlyphAdjustmentRecord(k.first,new UnityEngine.TextCore.LowLevel.GlyphValueRecord(0,0,k.advance,0)),
                    secondAdjustmentRecord=new UnityEngine.TextCore.LowLevel.GlyphAdjustmentRecord(k.second,new UnityEngine.TextCore.LowLevel.GlyphValueRecord(0,0,0,0))
                });
            }
            // Custom Atlas shader samples RGBA, retaining the source font's colored outline.
            var material = new Material(shader); material.name="BitmapFontMaterial";
            material.mainTexture=atlas; material.SetColor("_FaceColor",Color.white);
            font.material=material;
            AssetDatabase.CreateAsset(font,spec.fontPath);AssetDatabase.AddObjectToAsset(material,font);
            font.ReadFontAssetDefinition();EditorUtility.SetDirty(font);AssetDatabase.SaveAssetIfDirty(font);
            fonts[spec.id]=font;
        }
        // Additive preview scene preserves any previously open scene.
        var previous = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
        if(!EditorSceneManager.SaveScene(scene,BootstrapPath))throw new InvalidOperationException("Isolated bootstrap scene save failed");
        var canvas = new GameObject("MonkeyCandidate",typeof(RectTransform),typeof(Canvas),
            typeof(UnityEngine.UI.CanvasScaler),typeof(UnityEngine.UI.GraphicRaycaster));
        SceneManager.MoveGameObjectToScene(canvas,scene);
        canvas.layer=5;
        var cr = (RectTransform)canvas.transform;
        cr.pivot = Vector2.zero;
        canvas.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvas.GetComponent<UnityEngine.UI.CanvasScaler>();
        scaler.uiScaleMode = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(plan.designSize[0],plan.designSize[1]);
        scaler.matchWidthOrHeight = .5f;
        var designRoot = new GameObject("DesignRoot",typeof(RectTransform));
        designRoot.transform.SetParent(canvas.transform,false);
        var designRect=(RectTransform)designRoot.transform;
        designRect.anchorMin=designRect.anchorMax=new Vector2(.5f,.5f);designRect.pivot=Vector2.zero;
        designRect.sizeDelta=new Vector2(plan.designSize[0],plan.designSize[1]);
        designRect.anchoredPosition=-designRect.sizeDelta*.5f;
        var nodeMap = new Dictionary<string, GameObject>();
        foreach (var node in plan.nodes)
            nodeMap.Add(node.sourceId,new GameObject(node.name,typeof(RectTransform)) {layer=5});
        foreach (var node in plan.nodes)
        {
            var go = nodeMap[node.sourceId];
            var parent = node.parent != null && nodeMap.ContainsKey(node.parent) ? nodeMap[node.parent].transform : designRoot.transform;
            var rect = (RectTransform)go.transform;
            rect.SetParent(parent,false);
            var pr = parent as RectTransform;
            rect.anchorMin = rect.anchorMax = pr != null ? pr.pivot : Vector2.zero;
            rect.pivot = new Vector2(node.anchor[0],node.anchor[1]);
            rect.sizeDelta = new Vector2(node.size[0],node.size[1]);
            rect.anchoredPosition3D = new Vector3(node.position[0],node.position[1],node.position[2]);
            rect.localRotation = new Quaternion(node.rotation[0],node.rotation[1],node.rotation[2],node.rotation[3]);
            rect.localScale = new Vector3(node.scale[0],node.scale[1],node.scale[2]);
            go.SetActive(node.active);
            if (node.opacity != 255) {
                var opacity = go.AddComponent<CanvasGroup>();
                opacity.alpha = node.opacity / 255f;
            }
        }
        foreach (var node in plan.nodes)
            for (var i=0;i<node.children.Length;i++)
                if (nodeMap.ContainsKey(node.children[i])) nodeMap[node.children[i]].transform.SetSiblingIndex(i);
        var nodeSpecs = plan.nodes.ToDictionary(n=>n.sourceId);
        foreach (var spec in plan.components)
        {
            if (!spec.convertible || !nodeMap.ContainsKey(spec.node)) {
                diagnostics.Add("COMPONENT_NOT_IMPORTED: " + spec.sourceId + " " + spec.type); continue;
            }
            var go = nodeMap[spec.node]; var node = nodeSpecs[spec.node];
            var color = new Color(node.color[0]/255f,node.color[1]/255f,node.color[2]/255f,node.color[3]/255f);
            if (spec.type == "cc.Sprite")
            {
                var key = spec.spriteFrame + (spec.trim ? "" : "@original");
                if (spec.spriteFrame!=null && !spriteMap.ContainsKey(key)) { diagnostics.Add("SPRITE_MISSING: " + spec.sourceId); continue; }
                if (go.GetComponent<UnityEngine.UI.Graphic>() != null) {
                    diagnostics.Add("MULTIPLE_GRAPHICS_ON_NODE: " + spec.sourceId); continue;
                }
                var image = go.AddComponent<UnityEngine.UI.Image>();
                image.sprite = spec.spriteFrame==null?null:spriteMap[key]; image.color = color; image.raycastTarget = false;
                image.type = spec.mode == 1 ? UnityEngine.UI.Image.Type.Sliced : spec.mode==2 ? UnityEngine.UI.Image.Type.Tiled : UnityEngine.UI.Image.Type.Simple;
                image.enabled = spec.enabled && spec.spriteFrame!=null;
            }
            else if (spec.type == "cc.Label")
            {
                if (spec.font == null || !fonts.ContainsKey(spec.font)) {
                    diagnostics.Add("MATCHING_FONT_MISSING: " + spec.sourceId); continue;
                }
                if (go.GetComponent<UnityEngine.UI.Graphic>() != null) {
                    diagnostics.Add("MULTIPLE_GRAPHICS_ON_NODE: " + spec.sourceId); continue;
                }
                var label = go.AddComponent<TMPro.TextMeshProUGUI>();
                label.font = fonts[spec.font]; label.text = spec.text; label.fontSize = spec.fontSize;
                label.margin=spec.bitmapProbe==null?Vector4.zero:new Vector4(0,0,spec.bitmapProbe.inkRight-spec.bitmapProbe.advance,0);
                label.fontStyle = spec.bold ? TMPro.FontStyles.Bold : TMPro.FontStyles.Normal;
                label.characterSpacing=spec.fontSize>0?spec.spacing*100f/spec.fontSize:0;
                label.lineSpacing=spec.fontSize>0?(spec.lineHeight-fonts[spec.font].faceInfo.lineHeight*spec.fontSize/fonts[spec.font].faceInfo.pointSize)*100f/spec.fontSize:0;
                label.enableAutoSizing = false; label.richText = false; label.color = color;
                label.raycastTarget = false; label.enabled = spec.enabled;
                label.textWrappingMode = spec.wrap && spec.overflow!=0 ? TMPro.TextWrappingModes.Normal : TMPro.TextWrappingModes.NoWrap;
                var horizontal = new [] { TMPro.HorizontalAlignmentOptions.Left, TMPro.HorizontalAlignmentOptions.Center, TMPro.HorizontalAlignmentOptions.Right };
                var vertical = new [] { TMPro.VerticalAlignmentOptions.Top, TMPro.VerticalAlignmentOptions.Middle, TMPro.VerticalAlignmentOptions.Bottom };
                label.horizontalAlignment = horizontal[Mathf.Clamp(spec.horizontalAlign,0,2)];
                label.verticalAlignment = vertical[Mathf.Clamp(spec.verticalAlign,0,2)];
                diagnostics.Add("LABEL_LINE_METRICS_REQUIRE_REFERENCE: " + spec.sourceId);
            }
        }
        foreach(var spec in plan.components.Where(c=>c.convertible)) {
            var go=nodeMap[spec.node];var rect=(RectTransform)go.transform;
            if(spec.type=="cc.Widget" && spec.flags==45) {
                rect.anchorMin=Vector2.zero;rect.anchorMax=Vector2.one;
                rect.offsetMin=new Vector2(spec.margins[0],spec.margins[1]);
                rect.offsetMax=new Vector2(-spec.margins[2],-spec.margins[3]);
            }
            else if(spec.type=="cc.Mask") {
                var mask=go.AddComponent<UnityEngine.UI.RectMask2D>();mask.enabled=spec.enabled;
            }
            else if(spec.type=="cc.Layout") {
                var padding=new RectOffset((int)spec.padding[0],(int)spec.padding[2],(int)spec.padding[3],(int)spec.padding[1]);
                var fitter=go.AddComponent<UnityEngine.UI.ContentSizeFitter>();
                if(spec.layoutType==3) {
                    var group=go.AddComponent<UnityEngine.UI.GridLayoutGroup>();group.enabled=spec.enabled;
                    group.cellSize=new Vector2(spec.effectiveCellSize[0],spec.effectiveCellSize[1]);
                    group.spacing=new Vector2(spec.spacingXY[0],spec.spacingXY[1]);group.padding=padding;
                    group.startAxis=UnityEngine.UI.GridLayoutGroup.Axis.Horizontal;
                    group.startCorner=spec.verticalDirection==1?(spec.horizontalDirection==0?UnityEngine.UI.GridLayoutGroup.Corner.UpperLeft:UnityEngine.UI.GridLayoutGroup.Corner.UpperRight):
                        (spec.horizontalDirection==0?UnityEngine.UI.GridLayoutGroup.Corner.LowerLeft:UnityEngine.UI.GridLayoutGroup.Corner.LowerRight);
                    group.constraint=UnityEngine.UI.GridLayoutGroup.Constraint.Flexible;
                    fitter.verticalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
                }
                else {
                    UnityEngine.UI.HorizontalOrVerticalLayoutGroup group=spec.layoutType==1?
                        (UnityEngine.UI.HorizontalOrVerticalLayoutGroup)go.AddComponent<UnityEngine.UI.HorizontalLayoutGroup>():go.AddComponent<UnityEngine.UI.VerticalLayoutGroup>();
                    group.enabled=spec.enabled;group.padding=padding;
                    group.childControlWidth=false;group.childControlHeight=false;
                    group.childForceExpandWidth=false;group.childForceExpandHeight=false;
                    group.childAlignment=TextAnchor.MiddleCenter;
                    group.reverseArrangement=spec.layoutType==1?spec.horizontalDirection==1:spec.verticalDirection==0;
                    group.spacing=spec.layoutType==1?spec.spacingXY[0]:spec.spacingXY[1];
                    if(spec.layoutType==1)fitter.horizontalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
                    else fitter.verticalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
                }
                fitter.enabled=spec.enabled;
            }
            else if(spec.type=="cc.ScrollView") {
                var scroll=go.AddComponent<UnityEngine.UI.ScrollRect>();scroll.enabled=spec.enabled;
                scroll.content=(RectTransform)nodeMap[spec.content].transform;scroll.viewport=(RectTransform)scroll.content.parent;
                scroll.horizontal=spec.horizontal;scroll.vertical=spec.vertical;scroll.inertia=false;
            }
            else if(spec.type=="cc.Button") {
                var button=go.AddComponent<UnityEngine.UI.Button>();button.enabled=spec.enabled;button.interactable=spec.interactable;
                button.targetGraphic=go.GetComponent<UnityEngine.UI.Graphic>();
                if(button.targetGraphic!=null)button.targetGraphic.raycastTarget=true;
                button.transition=UnityEngine.UI.Selectable.Transition.None;
                if(spec.transition==3)ConfigureScaleButton(go,button,spec);
                // No callback stubs: actual source handlers remain in the handoff.
            }
            else if(spec.type=="cc.LabelOutline" && spec.enabled) {
                var label=go.GetComponent<TMPro.TextMeshProUGUI>();
                if(label==null) {diagnostics.Add("OUTLINE_LABEL_MISSING: "+spec.sourceId);continue;}
                if(plan.bitmapFonts.Any(f=>fonts.ContainsKey(f.id) && fonts[f.id]==label.font))continue;
                var material=new Material(label.fontSharedMaterial);
                var gradient=material.GetFloat("_GradientScale");
                var width=spec.width*label.font.faceInfo.pointSize/Mathf.Max(label.fontSize,1)/Mathf.Max(gradient,1);
                material.SetFloat("_OutlineWidth",Mathf.Clamp01(width));
                material.SetColor("_OutlineColor",new Color(spec.outlineColor[0]/255f,spec.outlineColor[1]/255f,spec.outlineColor[2]/255f,spec.outlineColor[3]/255f));
                var path="Assets/Generated/Art/"+spec.nativeId+".mat";AssetDatabase.CreateAsset(material,path);
                label.fontSharedMaterial=material;
                label.margin=new Vector4(spec.width,spec.width,spec.width,spec.width);
                label.UpdateMeshPadding();
            }
        }
        Canvas.ForceUpdateCanvases();
        UnityEngine.UI.LayoutRebuilder.ForceRebuildLayoutImmediate(designRect);
        if (plan.galleryOnly)
        {
            var i=0;
            foreach (var item in plan.textures.Where(t=>!t.id.EndsWith("@original"))) {
                var go=new GameObject("AssetPreview_"+i,typeof(RectTransform),typeof(UnityEngine.UI.Image));
                var rect=(RectTransform)go.transform;rect.SetParent(designRoot.transform,false);
                rect.anchorMin=rect.anchorMax=Vector2.zero; rect.pivot=new Vector2(.5f,.5f);
                rect.anchoredPosition=new Vector2(120+(i%3)*230,1130-(i/3)*230);
                rect.sizeDelta=new Vector2(180,180);
                var image=go.GetComponent<UnityEngine.UI.Image>();image.sprite=spriteMap[item.id];
                image.type=item.border.Any(v=>v>0)?UnityEngine.UI.Image.Type.Sliced:UnityEngine.UI.Image.Type.Simple;
                image.preserveAspect=image.type==UnityEngine.UI.Image.Type.Simple;image.raycastTarget=false;i++;
            }
        }
        var motionReadback=BuildMotions(plan,nodeMap);
        var view = canvas.AddComponent<MonkeyCandidateView>();
        view.Images = canvas.GetComponentsInChildren<UnityEngine.UI.Image>(true);
        view.Labels = canvas.GetComponentsInChildren<TMPro.TextMeshProUGUI>(true);
        view.Buttons = canvas.GetComponentsInChildren<UnityEngine.UI.Button>(true);
        var events=new GameObject("EventSystem",typeof(UnityEngine.EventSystems.EventSystem),typeof(UnityEngine.EventSystems.StandaloneInputModule));
        SceneManager.MoveGameObjectToScene(events,scene);
        var sourcePrefabResults=new List<SourcePrefabResult>();
        foreach(var spec in plan.sourcePrefabs ?? new SourcePrefabSpec[0]) {
            if(!spec.path.StartsWith("Assets/Generated/Views/Sources/",StringComparison.Ordinal) || spec.path.Contains("..") || File.Exists(spec.path))
                throw new InvalidOperationException("Invalid or existing source prefab path: "+spec.path);
            Directory.CreateDirectory(Path.GetDirectoryName(spec.path));
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var clone=UnityEngine.Object.Instantiate(nodeMap[spec.root].gameObject);
            clone.name=nodeMap[spec.root].name;
            try {
                var sourcePrefab=PrefabUtility.SaveAsPrefabAsset(clone,spec.path,out bool saved);
                if(!saved || sourcePrefab==null)throw new InvalidOperationException("Source prefab save failed: "+spec.sourceId);
            } finally { UnityEngine.Object.DestroyImmediate(clone); }
            var contents=PrefabUtility.LoadPrefabContents(spec.path);
            try {
                var transforms=contents.GetComponentsInChildren<Transform>(true);
                int missing=transforms.Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
                if(transforms.Length!=spec.nodeCount || missing!=0)throw new InvalidOperationException("Source prefab reopen mismatch: "+spec.sourceId);
                sourcePrefabResults.Add(new SourcePrefabResult {sourceId=spec.sourceId,path=spec.path,
                    guid=AssetDatabase.AssetPathToGUID(spec.path),nodeCount=transforms.Length,missingScripts=missing});
            } finally { PrefabUtility.UnloadPrefabContents(contents); }
        }
        var prefab = PrefabUtility.SaveAsPrefabAsset(canvas,PrefabPath,out var success);
        if (!success || prefab == null) throw new InvalidOperationException("Native Prefab save failed");
        UnityEngine.Object.DestroyImmediate(canvas);
        var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);
        if (!EditorSceneManager.SaveScene(scene,ScenePath)) throw new InvalidOperationException("Native scene save failed");
        var readback = new Readback {
            sourcePrefabs=sourcePrefabResults.ToArray(),
            jsonAssets=plan.assets.Where(a=>a.kind=="cc.JsonAsset").Select(a=> {
                var text=AssetDatabase.LoadAssetAtPath<TextAsset>(a.path);
                if(text==null)throw new InvalidOperationException("JsonAsset TextAsset import failed: "+a.id);
                using(var hash=System.Security.Cryptography.SHA256.Create())return new JsonResult {id=a.id,guid=AssetDatabase.AssetPathToGUID(a.path),
                    textSha256=BitConverter.ToString(hash.ComputeHash(System.Text.Encoding.UTF8.GetBytes(text.text))).Replace("-","").ToLowerInvariant()};
            }).ToArray(),
            status=diagnostics.Count==0?"imported":"partial",unityVersion=Application.unityVersion,
            prefabGuid=AssetDatabase.AssetPathToGUID(PrefabPath),sceneGuid=AssetDatabase.AssetPathToGUID(ScenePath),
            animations=motionReadback,spriteCount=spriteMap.Count,nodeCount=nodeMap.Count,
            missingScripts=instance.GetComponentsInChildren<Transform>(true).Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)),
            diagnostics=diagnostics.ToArray(),
            nodes=plan.nodes.Select(n=>{
                // Resolve saved Prefab contents; source objects have been destroyed.
                // Resolve by sibling-index path, not ambiguous display names.
                var indices=new List<int>(); var current=n;
                while(current.parent!=null && nodeSpecs.ContainsKey(current.parent)) {
                    var parent=nodeSpecs[current.parent]; indices.Add(Array.IndexOf(parent.children,current.sourceId));current=parent;
                }
                var roots=plan.nodes.Where(v=>v.parent==null || !nodeSpecs.ContainsKey(v.parent)).ToArray();
                var target=instance.transform.Find("DesignRoot").GetChild(Array.FindIndex(roots,v=>v.sourceId==current.sourceId));
                indices.Reverse();foreach(var index in indices)target=target.GetChild(index);
                var rect=(RectTransform)target;
                return new NodeResult {sourceId=n.sourceId,hierarchy=target.name,size=new[]{rect.rect.width,rect.rect.height},
                    pivot=new[]{rect.pivot.x,rect.pivot.y},position=new[]{rect.localPosition.x,rect.localPosition.y,rect.localPosition.z},
                    active=target.gameObject.activeSelf,componentTypes=target.GetComponents<Component>().Select(c=>c.GetType().FullName).ToArray()};
            }).ToArray(),
            fonts=fonts.Select(pair=>new FontResult { id=pair.Key,guid=AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(pair.Value)),
                glyphCount=pair.Value.glyphTable.Count,characterCount=pair.Value.characterTable.Count,
                pointSize=pair.Value.faceInfo.pointSize,lineHeight=pair.Value.faceInfo.lineHeight }).ToArray(),
            labels=plan.components.Where(c=>c.convertible && c.type=="cc.Label").Select(c=>{
                var label=SavedNode(nodeSpecs[c.node],plan.nodes,instance).GetComponent<TMPro.TextMeshProUGUI>();
                if(label==null)return new LabelResult {sourceId=c.sourceId,allCharactersPresent=false};
                label.ForceMeshUpdate(true,true);
                return new LabelResult {sourceId=c.sourceId,text=label.text,fontGuid=AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(label.font)),
                    fontSize=label.fontSize,characterCount=label.textInfo.characterCount,
                    glyphBounds=label.textInfo.characterInfo.Take(label.textInfo.characterCount).Where(info=>info.isVisible).Select(info=>new GlyphBounds {
                        unicode=info.character,left=info.bottomLeft.x,top=info.topLeft.y,width=info.topRight.x-info.topLeft.x,height=info.topLeft.y-info.bottomLeft.y
                    }).ToArray(),
                    allCharactersPresent=label.text.Where(ch=>!char.IsWhiteSpace(ch)).All(ch=>label.font.HasCharacter(ch))};
            }).ToArray(),
            sprites=plan.textures.Select(t=>{
                var s=spriteMap[t.id];AssetDatabase.TryGetGUIDAndLocalFileIdentifier(s,out string g,out long id);
                return new SpriteResult {id=t.id,guid=g,fileId=id,size=new[]{s.rect.width,s.rect.height},
                    border=new[]{s.border.x,s.border.y,s.border.z,s.border.w}};
            }).ToArray()
        };
        var savedView=instance.GetComponent<MonkeyCandidateView>();
        readback.viewReferences=plan.components.Where(c=>c.convertible && new[]{"cc.Sprite","cc.Label","cc.Button"}.Contains(c.type)).Select(c=> {
            var node=SavedNode(nodeSpecs[c.node],plan.nodes,instance);
            Component component=null;string field;int index;
            if(c.type=="cc.Sprite") {component=node.GetComponent<UnityEngine.UI.Image>();field="Images";index=Array.IndexOf(savedView.Images,component as UnityEngine.UI.Image);}
            else if(c.type=="cc.Label") {component=node.GetComponent<TMPro.TextMeshProUGUI>();field="Labels";index=Array.IndexOf(savedView.Labels,component as TMPro.TextMeshProUGUI);}
            else {component=node.GetComponent<UnityEngine.UI.Button>();field="Buttons";index=Array.IndexOf(savedView.Buttons,component as UnityEngine.UI.Button);}
            var source=component!=null?PrefabUtility.GetCorrespondingObjectFromSource(component):null;
            long fileId=0;if(source!=null)AssetDatabase.TryGetGUIDAndLocalFileIdentifier(source,out string ignoredGuid,out fileId);
            return new ViewReference {sourceId=c.sourceId,field=field,index=index,prefabFileId=fileId,bound=component!=null && index>=0};
        }).ToArray();
        readback.editableRoundtrip=CheckEditableClone();
        readback.colorSpace=QualitySettings.activeColorSpace.ToString();
        try {
            var preview="Analysis/native-page.png";
            Capture(instance.GetComponent<Canvas>(),scene,(int)plan.designSize[0],(int)plan.designSize[1],preview);
            readback.previewPath=preview;readback.previewSha256=Hash(preview);
        }
        catch(Exception exception) {readback.previewError=exception.Message;}
        if (!EditorSceneManager.SaveScene(scene,ScenePath)) throw new InvalidOperationException("Scene save after native preview failed");
        readback.nativeFiles = new[]{"Assets/Generated","Assets/TextMesh Pro"}.Where(Directory.Exists).SelectMany(folder=>Directory.GetFiles(folder,"*",SearchOption.AllDirectories))
            .Concat(Directory.GetFiles("Assets/Monkey","*.meta",SearchOption.AllDirectories))
            .OrderBy(path=>path,StringComparer.Ordinal).Select(path=>new FileResult {
                path=path.Replace('\\','/'), sha256=Hash(path)
            }).ToArray();
        Directory.CreateDirectory("Analysis");
        File.WriteAllText("Analysis/editor-readback.json",JsonUtility.ToJson(readback,true));
        Debug.Log("Monkey native import: "+readback.status+"; readback Analysis/editor-readback.json");
        if (previous.IsValid()) SceneManager.SetActiveScene(previous);
        // Keep the candidate scene open for editing; no global SaveAssets, no other scenes saved.
    }
    static bool CheckEditableClone() {
        const string path="Assets/Generated/Views/EditableProbe.prefab";
        if(!AssetDatabase.CopyAsset(PrefabPath,path))throw new InvalidOperationException("Native editable probe copy failed");
        var contents=PrefabUtility.LoadPrefabContents(path);var original=contents.transform.GetChild(0).name;
        try {
            contents.transform.GetChild(0).name=original+"__EditProbe";
            PrefabUtility.SaveAsPrefabAsset(contents,path,out bool saved);
            if(!saved)throw new InvalidOperationException("Native edit/save probe failed");
        }
        finally {PrefabUtility.UnloadPrefabContents(contents);}
        contents=PrefabUtility.LoadPrefabContents(path);
        try {
            bool persisted=contents.transform.GetChild(0).name==original+"__EditProbe";
            contents.transform.GetChild(0).name=original;
            PrefabUtility.SaveAsPrefabAsset(contents,path,out bool saved);
            return persisted && saved && contents.GetComponent<MonkeyCandidateView>()!=null;
        }
        finally {PrefabUtility.UnloadPrefabContents(contents);}
    }
    static void Capture(Canvas canvas,Scene scene,int width,int height,string output) {
        var cameraObject=new GameObject("MonkeyPreviewCamera",typeof(Camera));SceneManager.MoveGameObjectToScene(cameraObject,scene);
        var camera=cameraObject.GetComponent<Camera>();camera.enabled=false;camera.orthographic=true;camera.orthographicSize=height*.5f;
        camera.cullingMask=1<<5;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.1f,.11f,.13f,1);
        camera.transform.position=new Vector3(0,0,-10);camera.nearClipPlane=.1f;camera.farClipPlane=100;
        var target=new RenderTexture(width,height,24,RenderTextureFormat.ARGB32);target.Create();camera.targetTexture=target;
        var previousMode=canvas.renderMode;var previousCamera=canvas.worldCamera;var previousDistance=canvas.planeDistance;
        var previousActive=RenderTexture.active;Texture2D image=null;
        try {
            foreach(var transform in canvas.GetComponentsInChildren<Transform>(true))transform.gameObject.layer=5;
            canvas.renderMode=RenderMode.ScreenSpaceCamera;canvas.worldCamera=camera;canvas.planeDistance=1;
            Canvas.ForceUpdateCanvases();camera.Render();RenderTexture.active=target;
            image=new Texture2D(width,height,TextureFormat.RGBA32,false);
            image.ReadPixels(new Rect(0,0,width,height),0,0);image.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(output));File.WriteAllBytes(output,image.EncodeToPNG());
        }
        finally {
            canvas.renderMode=previousMode;canvas.worldCamera=previousCamera;canvas.planeDistance=previousDistance;
            RenderTexture.active=previousActive;camera.targetTexture=null;
            target.Release();UnityEngine.Object.DestroyImmediate(target);UnityEngine.Object.DestroyImmediate(cameraObject);
            if(image!=null)UnityEngine.Object.DestroyImmediate(image);
            Canvas.ForceUpdateCanvases();
        }
    }
    static void ConfigureScaleButton(GameObject go,UnityEngine.UI.Button button,ComponentSpec spec) {
        var path="Assets/Generated/Controllers/"+spec.nativeId;
        var controller=UnityEditor.Animations.AnimatorController.CreateAnimatorControllerAtPath(path+".controller");
        var normal=new AnimationClip {name="Normal"};var pressed=new AnimationClip {name="Pressed"};
        var scale=go.transform.localScale;
        foreach(var axis in new[]{"x","y","z"}) {
            var value=axis=="x"?scale.x:axis=="y"?scale.y:scale.z;
            normal.SetCurve("",typeof(Transform),"m_LocalScale."+axis,AnimationCurve.Constant(0,Mathf.Max(spec.duration,.001f),value));
            pressed.SetCurve("",typeof(Transform),"m_LocalScale."+axis,AnimationCurve.Constant(0,Mathf.Max(spec.duration,.001f),value*spec.zoomScale));
        }
        AssetDatabase.CreateAsset(normal,path+"-normal.anim");AssetDatabase.CreateAsset(pressed,path+"-pressed.anim");
        var machine=controller.layers[0].stateMachine;
        foreach(var trigger in new[]{"Normal","Highlighted","Pressed","Selected","Disabled"}) {
            controller.AddParameter(trigger,AnimatorControllerParameterType.Trigger);
            var state=machine.AddState(trigger);state.motion=trigger=="Pressed"?pressed:normal;
            var transition=machine.AddAnyStateTransition(state);transition.AddCondition(UnityEditor.Animations.AnimatorConditionMode.If,0,trigger);
            transition.hasExitTime=false;transition.hasFixedDuration=true;transition.duration=spec.duration;transition.canTransitionToSelf=false;
            if(trigger=="Normal")machine.defaultState=state;
        }
        var animator=go.AddComponent<Animator>();animator.runtimeAnimatorController=controller;
        button.transition=UnityEngine.UI.Selectable.Transition.Animation;
        EditorUtility.SetDirty(controller);AssetDatabase.SaveAssetIfDirty(controller);
    }
    static RectTransform SavedNode(NodeSpec node,NodeSpec[] nodes,GameObject instance) {
        var byId=nodes.ToDictionary(n=>n.sourceId); var indices=new List<int>(); var current=node;
        while(current.parent!=null && byId.ContainsKey(current.parent)) {
            var parent=byId[current.parent]; indices.Add(Array.IndexOf(parent.children,current.sourceId)); current=parent;
        }
        var roots=nodes.Where(n=>n.parent==null || !byId.ContainsKey(n.parent)).ToArray();
        var target=instance.transform.Find("DesignRoot").GetChild(Array.FindIndex(roots,n=>n.sourceId==current.sourceId));
        indices.Reverse();foreach(var index in indices)target=target.GetChild(index);
        return (RectTransform)target;
    }
    static string Hash(string path) {
        using (var algorithm = System.Security.Cryptography.SHA256.Create())
        using (var input = File.OpenRead(path))
            return BitConverter.ToString(algorithm.ComputeHash(input)).Replace("-","").ToLowerInvariant();
    }

    static MotionResult[] BuildMotions(Plan plan,Dictionary<string,GameObject> nodes) {
        var results=new List<MotionResult>();
        foreach(var spec in plan.animations ?? Array.Empty<MotionSpec>()) {
            if(!spec.convertible)continue;
            if(!spec.path.StartsWith("Assets/Generated/Animations/") || spec.path.Contains("..") || File.Exists(spec.path))
                throw new InvalidOperationException("Unsafe/existing animation output: "+spec.path);
            Directory.CreateDirectory("Assets/Generated/Animations");
            var clip=new AnimationClip {name=spec.name,frameRate=spec.sample};
            foreach(var track in spec.tracks) {
                if(AnimationUtility.CalculateTransformPath(nodes[track.node].transform,nodes[spec.root].transform)!=track.path)
                    throw new InvalidOperationException("Animation hierarchy mismatch");
                var type=track.nativeType=="CanvasGroup"?typeof(CanvasGroup):track.nativeType=="RectTransform"?typeof(RectTransform):typeof(Transform);
                if(type==typeof(CanvasGroup) && nodes[track.node].GetComponent<CanvasGroup>()==null)nodes[track.node].AddComponent<CanvasGroup>();
                var curve=new AnimationCurve(track.keys.Select(k=>new Keyframe(k.time,k.value)).ToArray());
                curve.preWrapMode=curve.postWrapMode=WrapMode.ClampForever;
                for(var i=0;i<track.keys.Length;i++) {
                    AnimationUtility.SetKeyBroken(curve,i,true);
                    AnimationUtility.SetKeyLeftTangentMode(curve,i,AnimationUtility.TangentMode.Linear);
                    AnimationUtility.SetKeyRightTangentMode(curve,i,track.keys[i].interpolation=="step"?AnimationUtility.TangentMode.Constant:AnimationUtility.TangentMode.Linear);
                }
                for(var i=1;i<track.keys.Length;i++)AnimationUtility.SetKeyLeftTangentMode(curve,i,track.keys[i-1].interpolation=="step"?AnimationUtility.TangentMode.Constant:AnimationUtility.TangentMode.Linear);
                AnimationUtility.SetEditorCurve(clip,EditorCurveBinding.FloatCurve(track.path,type,track.nativeProperty),curve);
            }
            var settings=AnimationUtility.GetAnimationClipSettings(clip);settings.loopTime=spec.wrap=="loop";
            AnimationUtility.SetAnimationClipSettings(clip,settings);AnimationUtility.SetAnimationEvents(clip,Array.Empty<AnimationEvent>());
            AssetDatabase.CreateAsset(clip,spec.path);EditorUtility.SetDirty(clip);AssetDatabase.SaveAssetIfDirty(clip);
            AssetDatabase.ImportAsset(spec.path,ImportAssetOptions.ForceUpdate);
            var saved=AssetDatabase.LoadAssetAtPath<AnimationClip>(spec.path);
            results.Add(new MotionResult {id=spec.id,path=spec.path,guid=AssetDatabase.AssetPathToGUID(spec.path),duration=saved.length,
                wrap=AnimationUtility.GetAnimationClipSettings(saved).loopTime?"loop":"normal",eventCount=AnimationUtility.GetAnimationEvents(saved).Length,curveCount=AnimationUtility.GetCurveBindings(saved).Length,
                tracks=spec.tracks.Select(track=>{
                    var type=track.nativeType=="CanvasGroup"?typeof(CanvasGroup):track.nativeType=="RectTransform"?typeof(RectTransform):typeof(Transform);
                    var curve=AnimationUtility.GetEditorCurve(saved,EditorCurveBinding.FloatCurve(track.path,type,track.nativeProperty));
                    return new MotionTrackResult {path=track.path,property=track.nativeProperty,nativeType=track.nativeType,
                        times=curve.keys.Select(k=>k.time).ToArray(),values=curve.keys.Select(k=>k.value).ToArray(),
                        interpolations=Enumerable.Range(0,curve.length).Select(i=>AnimationUtility.GetKeyRightTangentMode(curve,i)==AnimationUtility.TangentMode.Constant?"step":AnimationUtility.GetKeyRightTangentMode(curve,i)==AnimationUtility.TangentMode.Linear?"linear":"unsupported").ToArray(),
                        probeTimes=track.probes.Select(p=>p.time).ToArray(),probeValues=track.probes.Select(p=>curve.Evaluate(p.time)).ToArray()};
                }).ToArray()});
        }
        return results.ToArray();
    }

}
