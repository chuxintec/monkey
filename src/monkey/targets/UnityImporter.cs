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
        public TextureSpec[] textures; public AssetSpec[] assets; public int sourceDiagnosticCount;
        public NodeSpec[] nodes; public ComponentSpec[] components; public bool galleryOnly;
    }
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
        public int mode, sizeMode, fontSize, lineHeight, horizontalAlign, verticalAlign, overflow;
        public bool enabled, convertible, trim, wrap;
    }
    [Serializable] public class Readback {
        public string status, unityVersion, prefabGuid, sceneGuid;
        public int spriteCount, nodeCount, missingScripts;
        public string[] diagnostics; public NodeResult[] nodes; public SpriteResult[] sprites; public FileResult[] nativeFiles;
    }
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

    [MenuItem("Tools/Monkey/Import Candidate")]
    public static void ImportCandidate() { Run(); }
    public static void ImportBatch() { Run(); }

    static void Run()
    {
        if (Application.unityVersion != "6000.6.2f1")
            throw new InvalidOperationException("Candidate requires Unity 6000.6.2f1; no automatic version migration");
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Editor must be idle");
        if (File.Exists(PrefabPath) || File.Exists(ScenePath))
            throw new InvalidOperationException("Create-only import: Prefab/Scene already exists. Use a new candidate.");
        if (SceneManager.GetActiveScene().isDirty)
            throw new InvalidOperationException("Active scene has unsaved work; import refused");
        var plan = JsonUtility.FromJson<Plan>(File.ReadAllText("Assets/Monkey/Editor/import-plan.json"));
        var diagnostics = new List<string>();
        if (plan.sourceDiagnosticCount > 0) diagnostics.Add("SOURCE_GAPS: " + plan.sourceDiagnosticCount);
        var spriteMap = new Dictionary<string, Sprite>();
        foreach (var item in plan.textures)
        {
            var importer = AssetImporter.GetAtPath(item.path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException("Missing texture importer: " + item.path);
            importer.textureType = TextureImporterType.Sprite;
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
            var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(item.path);
            if (sprite == null) throw new InvalidOperationException("Sprite import failed: " + item.path);
            spriteMap.Add(item.id,sprite);
        }
        var fonts = new Dictionary<string, TMPro.TMP_FontAsset>();
        foreach (var item in plan.assets.Where(a => a.path.EndsWith(".ttf", StringComparison.OrdinalIgnoreCase)))
        {
            var source = AssetDatabase.LoadAssetAtPath<Font>(item.path);
            if (source == null) { diagnostics.Add("FONT_IMPORT_FAILED: " + item.id); continue; }
            if (Shader.Find("TextMeshPro/Distance Field") == null) {
                diagnostics.Add("TMP_SHADER_RESOURCES_MISSING: " + item.id); continue;
            }
            var font = TMPro.TMP_FontAsset.CreateFontAsset(source);
            if (font == null) { diagnostics.Add("TMP_FONT_CREATION_FAILED: " + item.id); continue; }
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
        // Additive preview scene preserves any previously open scene.
        var previous = SceneManager.GetActiveScene();
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Additive);
        var canvas = new GameObject("MonkeyCandidate",typeof(RectTransform),typeof(Canvas),
            typeof(UnityEngine.UI.CanvasScaler),typeof(UnityEngine.UI.GraphicRaycaster));
        SceneManager.MoveGameObjectToScene(canvas,scene);
        var cr = (RectTransform)canvas.transform;
        cr.pivot = Vector2.zero;
        canvas.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvas.GetComponent<UnityEngine.UI.CanvasScaler>();
        scaler.uiScaleMode = UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(plan.designSize[0],plan.designSize[1]);
        scaler.matchWidthOrHeight = .5f;
        var nodeMap = new Dictionary<string, GameObject>();
        foreach (var node in plan.nodes)
            nodeMap.Add(node.sourceId,new GameObject(node.name,typeof(RectTransform)));
        foreach (var node in plan.nodes)
        {
            var go = nodeMap[node.sourceId];
            var parent = node.parent != null && nodeMap.ContainsKey(node.parent) ? nodeMap[node.parent].transform : canvas.transform;
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
                if (!spriteMap.ContainsKey(key)) { diagnostics.Add("SPRITE_MISSING: " + spec.sourceId); continue; }
                if (go.GetComponent<UnityEngine.UI.Graphic>() != null) {
                    diagnostics.Add("MULTIPLE_GRAPHICS_ON_NODE: " + spec.sourceId); continue;
                }
                var image = go.AddComponent<UnityEngine.UI.Image>();
                image.sprite = spriteMap[key]; image.color = color; image.raycastTarget = false;
                image.type = spec.mode == 1 ? UnityEngine.UI.Image.Type.Sliced : UnityEngine.UI.Image.Type.Simple;
                image.enabled = spec.enabled;
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
                label.enableAutoSizing = false; label.richText = false; label.color = color;
                label.raycastTarget = false; label.enabled = spec.enabled;
                label.textWrappingMode = spec.wrap ? TMPro.TextWrappingModes.Normal : TMPro.TextWrappingModes.NoWrap;
                var horizontal = new [] { TMPro.HorizontalAlignmentOptions.Left, TMPro.HorizontalAlignmentOptions.Center, TMPro.HorizontalAlignmentOptions.Right };
                var vertical = new [] { TMPro.VerticalAlignmentOptions.Top, TMPro.VerticalAlignmentOptions.Middle, TMPro.VerticalAlignmentOptions.Bottom };
                label.horizontalAlignment = horizontal[Mathf.Clamp(spec.horizontalAlign,0,2)];
                label.verticalAlignment = vertical[Mathf.Clamp(spec.verticalAlign,0,2)];
                diagnostics.Add("LABEL_LINE_METRICS_REQUIRE_REFERENCE: " + spec.sourceId);
            }
        }
        if (plan.galleryOnly)
        {
            var i=0;
            foreach (var item in plan.textures.Where(t=>!t.id.EndsWith("@original"))) {
                var go=new GameObject("AssetPreview_"+i,typeof(RectTransform),typeof(UnityEngine.UI.Image));
                var rect=(RectTransform)go.transform;rect.SetParent(canvas.transform,false);
                rect.anchorMin=rect.anchorMax=Vector2.zero; rect.pivot=new Vector2(.5f,.5f);
                rect.anchoredPosition=new Vector2(120+(i%3)*230,1130-(i/3)*230);
                rect.sizeDelta=new Vector2(180,180);
                var image=go.GetComponent<UnityEngine.UI.Image>();image.sprite=spriteMap[item.id];
                image.type=item.border.Any(v=>v>0)?UnityEngine.UI.Image.Type.Sliced:UnityEngine.UI.Image.Type.Simple;
                image.preserveAspect=image.type==UnityEngine.UI.Image.Type.Simple;image.raycastTarget=false;i++;
            }
        }
        var view = canvas.AddComponent<MonkeyCandidateView>();
        view.Images = canvas.GetComponentsInChildren<UnityEngine.UI.Image>(true);
        view.Labels = canvas.GetComponentsInChildren<TMPro.TextMeshProUGUI>(true);
        view.Buttons = canvas.GetComponentsInChildren<UnityEngine.UI.Button>(true);
        var prefab = PrefabUtility.SaveAsPrefabAsset(canvas,PrefabPath,out var success);
        if (!success || prefab == null) throw new InvalidOperationException("Native Prefab save failed");
        UnityEngine.Object.DestroyImmediate(canvas);
        var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);
        if (!EditorSceneManager.SaveScene(scene,ScenePath)) throw new InvalidOperationException("Native scene save failed");
        var readback = new Readback {
            status=diagnostics.Count==0?"imported":"partial",unityVersion=Application.unityVersion,
            prefabGuid=AssetDatabase.AssetPathToGUID(PrefabPath),sceneGuid=AssetDatabase.AssetPathToGUID(ScenePath),
            spriteCount=spriteMap.Count,nodeCount=nodeMap.Count,
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
                var target=instance.transform.GetChild(Array.FindIndex(roots,v=>v.sourceId==current.sourceId));
                indices.Reverse();foreach(var index in indices)target=target.GetChild(index);
                var rect=(RectTransform)target;
                return new NodeResult {sourceId=n.sourceId,hierarchy=target.name,size=new[]{rect.sizeDelta.x,rect.sizeDelta.y},
                    pivot=new[]{rect.pivot.x,rect.pivot.y},position=new[]{rect.anchoredPosition3D.x,rect.anchoredPosition3D.y,rect.anchoredPosition3D.z},
                    active=target.gameObject.activeSelf,componentTypes=target.GetComponents<Component>().Select(c=>c.GetType().FullName).ToArray()};
            }).ToArray(),
            sprites=plan.textures.Select(t=>{
                var s=spriteMap[t.id];AssetDatabase.TryGetGUIDAndLocalFileIdentifier(s,out string g,out long id);
                return new SpriteResult {id=t.id,guid=g,fileId=id,size=new[]{s.rect.width,s.rect.height},
                    border=new[]{s.border.x,s.border.y,s.border.z,s.border.w}};
            }).ToArray()
        };
        readback.nativeFiles = Directory.GetFiles("Assets/Generated","*",SearchOption.AllDirectories)
            .OrderBy(path=>path,StringComparer.Ordinal).Select(path=>new FileResult {
                path=path.Replace('\\','/'), sha256=Hash(path)
            }).ToArray();
        Directory.CreateDirectory("Analysis");
        File.WriteAllText("Analysis/editor-readback.json",JsonUtility.ToJson(readback,true));
        Debug.Log("Monkey native import: "+readback.status+"; readback Analysis/editor-readback.json");
        if (previous.IsValid()) SceneManager.SetActiveScene(previous);
        // Keep the candidate scene open for editing; no global SaveAssets, no other scenes saved.
    }
    static string Hash(string path) {
        using (var algorithm = System.Security.Cryptography.SHA256.Create())
        using (var input = File.OpenRead(path))
            return BitConverter.ToString(algorithm.ComputeHash(input)).Replace("-","").ToLowerInvariant();
    }

}
