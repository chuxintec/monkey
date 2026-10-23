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
        public NodeSpec[] nodes; public ComponentSpec[] components; public MotionSpec[] animations; public bool galleryOnly; public SourcePrefabSpec[] sourcePrefabs; public TmpResourceSpec tmpResources;
    }
    [Serializable] public class TmpResourceSpec { public string packageName,packageVersion,resource,importMode; }
    [Serializable] public class TmpResourceResult {
        public int schemaVersion=1;public string status,packageName,packageVersion,source,resource,archiveSha256;
        public string bitmapGuid,distanceGuid,mobileGuid,settingsGuid,completionProof;
    }
    static Shader tmpBitmapShader,tmpDistanceShader;
    static TmpResourceResult tmpResourceResult;
    [Serializable] public class SourcePrefabSpec { public string sourceId,root,path; public string[] nodes; public int nodeCount; }
    [Serializable] public class SourcePrefabResult {
        public string sourceId,path,guid,geometryPhase; public int nodeCount,missingScripts,layoutSettlePasses;
        public bool savedReloaded,referencesVerified; public NodeResult[] nodes; public string[] referenceFailures;
    }
    [Serializable] public class MotionKey { public float time,value; public string interpolation; }
    [Serializable] public class MotionProbe { public float time,value; }
    [Serializable] public class MotionTrack { public string node,path,nativeType,nativeProperty; public MotionKey[] keys; public MotionProbe[] probes; }
    [Serializable] public class MotionSpec { public string id,name,root,path,wrap; public float duration,sample; public bool convertible; public MotionTrack[] tracks; }
    [Serializable] public class MotionTrackResult { public string path,property,nativeType; public float[] times,values,probeTimes,probeValues; public string[] interpolations; }
    [Serializable] public class MotionResult { public string id,path,guid,wrap; public float duration; public int eventCount,curveCount; public MotionTrackResult[] tracks; }
    [Serializable] public class TextureSpec {
        public string id, path; public float[] border, size, originalSize, offset;
    }
    [Serializable] public class AssetSpec { public string id, kind, path, fontAssetPath; }
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
        public bool crossAxisScale; public float crossAxisAlignment;
    }
    [Serializable] public class BitmapProbe { public float advance,inkRight; }
    [Serializable] public class BitmapSpec {
        public string id, path, fontPath, atlasGuid; public float pointSize, lineHeight, ascent, descent;
        public int[] atlasSize; public GlyphSpec[] glyphs; public KerningSpec[] kernings;
    }
    [Serializable] public class GlyphSpec { public uint unicode, index; public int[] rect; public float[] metrics; }
    [Serializable] public class KerningSpec { public uint first, second; public float advance; }
    [Serializable] public class FontResult { public string id, guid, atlasGuid, materialAtlasGuid; public int glyphCount, characterCount; public float pointSize, lineHeight; }
    [Serializable] public class LabelResult { public string sourceId, text, fontGuid, geometryProbe; public float fontSize; public int characterCount; public bool allCharactersPresent; public GlyphBounds[] glyphBounds; }
    [Serializable] public class GlyphBounds { public uint unicode; public float left,top,width,height,quadPadding; }
    [Serializable] public class Readback {
        public string status, unityVersion, prefabGuid, sceneGuid;
        public int spriteCount, nodeCount, missingScripts; public bool editableRoundtrip,sceneReopened; public string previewPath,previewSha256,previewError,colorSpace;
        public MotionResult[] animations; public string[] diagnostics; public NodeResult[] nodes; public SpriteResult[] sprites; public FileResult[] nativeFiles; public FontResult[] fonts; public LabelResult[] labels; public ViewReference[] viewReferences; public JsonResult[] jsonAssets; public SourcePrefabResult[] sourcePrefabs; public TmpResourceResult tmpResources;
    }
    [Serializable] public class JsonResult { public string id,guid,textSha256; }
    [Serializable] public class ViewReference { public string sourceId,field; public int index; public long prefabFileId; public bool bound; }
    [Serializable] public class FileResult { public string path, sha256; }
    [Serializable] public class NodeResult {
        public string sourceId, hierarchy; public float[] size, pivot, position,scale,rotation;
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
    public static void ImportCandidate() { BeginAsync(Application.isBatchMode); }
    public static void ImportBatch() { ExecuteImport(); }
    public static void ImportBatchAsync() { BeginAsync(true); }

    [Serializable] public class NativeProgress {
        public int schemaVersion=1,processed,total;
        public string status,phase,planSha256; public double elapsedSeconds;
        public bool nativeResumeSupported=false;
    }
    static System.Diagnostics.Stopwatch nativeClock;
    static NativeProgress nativeProgress;
    static DateTime nativeDeadline=DateTime.MaxValue;
    static double nativeBudget=0;
    static Scene ownedScene;
    static Scene priorScene;
    static string firstEngineError;
    static bool handlingFailure;
    [Serializable] public class EngineErrorResult {public int schemaVersion=1;public string planSha256,phase,logType,errorSha256;}
    static void CaptureEngineError(string condition,string stack,LogType type) {
        if(handlingFailure || firstEngineError!=null || (type!=LogType.Error && type!=LogType.Exception && type!=LogType.Assert))return;
        using(var hash=System.Security.Cryptography.SHA256.Create())
            firstEngineError=BitConverter.ToString(hash.ComputeHash(System.Text.Encoding.UTF8.GetBytes(condition+"\n"+stack))).Replace("-","").ToLowerInvariant();
        // Keep messages/stack in the private Editor log, never copy authentication or user text into telemetry.
        try {
            Directory.CreateDirectory("Analysis");
            File.WriteAllText("Analysis/native-engine-error.json",JsonUtility.ToJson(new EngineErrorResult {
                planSha256=nativeProgress.planSha256,phase=nativeProgress.phase,logType=type.ToString(),errorSha256=firstEngineError},true));
        } catch { /* The captured flag still stops work if telemetry cannot be written. */ }
    }
    static void CheckEngineErrors() {
        if(firstEngineError!=null)throw new InvalidOperationException("NATIVE_ENGINE_ERROR_RECORDED: inspect the private Editor log and Analysis/native-engine-error.json");
    }

    static bool asyncRunning,asyncBatch,packagePending,tmpImportCompleted;
    static double nextAsyncTick;
    static void InitializeImport() {
        Application.logMessageReceived-=CaptureEngineError;firstEngineError=null;handlingFailure=false;
        ownedScene=default(Scene);priorScene=default(Scene);nativeProgress=null;
        nativeClock=System.Diagnostics.Stopwatch.StartNew();
        nativeProgress=new NativeProgress {status="running",phase="preflight",planSha256=Hash("Assets/Monkey/Editor/import-plan.json")};
        nativeDeadline=DateTime.MaxValue;nativeBudget=0;ownedScene=default(Scene);priorScene=default(Scene);tmpBitmapShader=null;tmpDistanceShader=null;tmpResourceResult=null;
            var budget=Environment.GetEnvironmentVariable("MONKEY_NATIVE_BUDGET_SECONDS");
            if(!string.IsNullOrEmpty(budget) && (!double.TryParse(budget,System.Globalization.NumberStyles.Float,System.Globalization.CultureInfo.InvariantCulture,out nativeBudget) || double.IsNaN(nativeBudget) || double.IsInfinity(nativeBudget) || nativeBudget<1 || nativeBudget>3600))
                throw new InvalidOperationException("Native budget must be 1..3600 seconds");
            var deadline=Environment.GetEnvironmentVariable("MONKEY_NATIVE_DEADLINE_UTC");
            if(!string.IsNullOrEmpty(deadline) && !DateTime.TryParse(deadline,System.Globalization.CultureInfo.InvariantCulture,System.Globalization.DateTimeStyles.AssumeUniversal|System.Globalization.DateTimeStyles.AdjustToUniversal,out nativeDeadline))
                throw new InvalidOperationException("Invalid native deadline");
        Application.logMessageReceived+=CaptureEngineError;

    }
    static void ExecuteImport() {
        if(asyncRunning)throw new InvalidOperationException("An import is already pending in this Editor");
        tmpImportCompleted=false;
        try {InitializeImport();NativeCheckpoint("preflight",0,1);Run();}
        catch(OperationCanceledException) {WriteNativeProgress("budget_exhausted");CloseOwnedScene();}
        catch {if(nativeProgress!=null)WriteNativeProgress("failed");CloseOwnedScene();throw;}
        finally {Application.logMessageReceived-=CaptureEngineError;}
    }
    static void BeginAsync(bool batch) {
        if(asyncRunning)throw new InvalidOperationException("An import is already pending in this Editor");
        asyncRunning=true;asyncBatch=batch;packagePending=false;tmpImportCompleted=false;nextAsyncTick=0;
        try {
            InitializeImport();ValidateEditorContext();
            if(batch && (!Application.isBatchMode || Environment.GetCommandLineArgs().Any(a=>a.StartsWith("-",StringComparison.Ordinal) && a.TrimStart('-').Split('=')[0].Equals("quit",StringComparison.OrdinalIgnoreCase))))
                throw new InvalidOperationException("ASYNC_ENTRYPOINT_REQUIRES_BATCH_WITHOUT_QUIT: use monkey native-import");
            NativeCheckpoint("preflight",0,1);
            EditorApplication.update+=CheckAsyncBudget;
            var plan=JsonUtility.FromJson<Plan>(File.ReadAllText("Assets/Monkey/Editor/import-plan.json"));
            if(NeedsTmp(plan) && !TmpFilesPresent()) {
                NativeCheckpoint("tmp-resources",0,1);
                var archive=ResolveTmpArchive(plan.tmpResources);
                tmpResourceResult.status="import_pending";WriteTmpResourceResult();packagePending=true;
                AssetDatabase.importPackageCompleted+=TmpPackageCompleted;
                AssetDatabase.importPackageFailed+=TmpPackageFailed;
                AssetDatabase.importPackageCancelled+=TmpPackageCancelled;
                UnityEditor.AssetPackage.Package.Import(archive,false);
                return; // Return to the Editor event loop; no -quit, busy wait or sleeping on the main thread.
            }
            EditorApplication.delayCall+=ContinueAsync;
        } catch(Exception error) {FailAsync(error);}
    }
    static void DetachPackageCallbacks() {
        AssetDatabase.importPackageCompleted-=TmpPackageCompleted;
        AssetDatabase.importPackageFailed-=TmpPackageFailed;
        AssetDatabase.importPackageCancelled-=TmpPackageCancelled;
    }
    static void TmpPackageCompleted(string name) {
        if(!asyncRunning || !packagePending || name!="TMP Essential Resources")return;
        try {
            packagePending=false;tmpImportCompleted=true;DetachPackageCallbacks();
            tmpResourceResult.status="import_completed";WriteTmpResourceResult();
            EditorApplication.delayCall+=ContinueAsync;
        } catch(Exception error) {FailAsync(error);}
    }
    static void TmpPackageFailed(string name,string message) {
        if(asyncRunning && packagePending && name=="TMP Essential Resources") {
            try {tmpResourceResult.status="import_failed";WriteTmpResourceResult();}
            finally {FailAsync(new InvalidOperationException("TMP_ESSENTIAL_IMPORT_FAILED: package completion failed"));}
        }
    }
    static void TmpPackageCancelled(string name) {
        if(asyncRunning && packagePending && name=="TMP Essential Resources") {
            try {tmpResourceResult.status="import_cancelled";WriteTmpResourceResult();}
            finally {FailAsync(new InvalidOperationException("TMP_ESSENTIAL_IMPORT_CANCELLED: package import cancelled"));}
        }
    }
    static void CheckAsyncBudget() {
        if(!asyncRunning || nativeClock.Elapsed.TotalSeconds<nextAsyncTick)return;
        nextAsyncTick=nativeClock.Elapsed.TotalSeconds+1;
        try {NativeCheckpoint(nativeProgress.phase,nativeProgress.processed,nativeProgress.total);}
        catch(Exception error) {FailAsync(error);}
    }
    static void ContinueAsync() {
        if(!asyncRunning || packagePending)return;
        try {
            NativeCheckpoint("tmp-resources",tmpImportCompleted?1:0,1);
            if(Hash("Assets/Monkey/Editor/import-plan.json")!=nativeProgress.planSha256)
                throw new InvalidOperationException("IMPORT_PLAN_CHANGED_WHILE_PENDING");
            Run();FinishAsync(0);
        } catch(Exception error) {FailAsync(error);}
    }
    static void FailAsync(Exception error) {
        if(!asyncRunning)return;
        handlingFailure=true;
        try {if(nativeProgress!=null)WriteNativeProgress(error is OperationCanceledException?"budget_exhausted":"failed");}
        finally {try {CloseOwnedScene();} finally {Debug.LogException(error);FinishAsync(error is OperationCanceledException?3:1);}}
    }
    static void FinishAsync(int exitCode) {
        bool ownsBatch=asyncBatch;asyncRunning=false;packagePending=false;
        DetachPackageCallbacks();EditorApplication.update-=CheckAsyncBudget;EditorApplication.delayCall-=ContinueAsync;
        Application.logMessageReceived-=CaptureEngineError;
        if(ownsBatch && Application.isBatchMode)EditorApplication.Exit(exitCode);
    }
    static void CloseOwnedScene() {
        if(priorScene.IsValid() && priorScene.isLoaded)SceneManager.SetActiveScene(priorScene);
        if(ownedScene.IsValid() && ownedScene.isLoaded) {
            if(SceneManager.sceneCount>1)EditorSceneManager.CloseScene(ownedScene,true);
            else EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        }
    }
    static void WriteNativeProgress(string status) {
        nativeProgress.status=status;nativeProgress.elapsedSeconds=nativeClock.Elapsed.TotalSeconds;
        Directory.CreateDirectory("Analysis");
        const string path="Analysis/native-progress.json";const string temporary=path+".tmp";
        File.WriteAllText(temporary,JsonUtility.ToJson(nativeProgress,true));
        if(File.Exists(path))File.Replace(temporary,path,null);else File.Move(temporary,path);
    }
    static void NativeCheckpoint(string phase,int processed,int total) {
        CheckEngineErrors();
        nativeProgress.phase=phase;nativeProgress.processed=processed;nativeProgress.total=total;
        if((nativeBudget>0 && nativeClock.Elapsed.TotalSeconds>=nativeBudget) || DateTime.UtcNow>=nativeDeadline) {
            WriteNativeProgress("budget_exhausted");throw new OperationCanceledException("Native import time budget exhausted");
        }
        WriteNativeProgress("running");
    }
    static Dictionary<string,Sprite> ImportTextures(Plan plan) {
        var sprites=new Dictionary<string,Sprite>();
        const int batchSize=128;
        NativeCheckpoint("textures",0,plan.textures.Length);
        for(int start=0;start<plan.textures.Length;start+=batchSize) {
            NativeCheckpoint("texture-settings",start,plan.textures.Length);
            var batch=plan.textures.Skip(start).Take(batchSize).ToArray();
            // Resolve existing importers before pausing imports; never load unfinished assets inside a batch.
            var importers=new Dictionary<string,TextureImporter>();
            foreach(var item in batch) {
                var importer=AssetImporter.GetAtPath(item.path) as TextureImporter;
                if(importer==null) {
                    AssetDatabase.ImportAsset(item.path,ImportAssetOptions.ForceUpdate|ImportAssetOptions.ForceSynchronousImport);
                    importer=AssetImporter.GetAtPath(item.path) as TextureImporter;
                }
                if(importer==null)throw new InvalidOperationException("Missing texture importer: "+item.path);
                importers.Add(item.id,importer);
            }
            AssetDatabase.StartAssetEditing();
            try {
                foreach(var item in batch) {
                    var importer=importers[item.id];
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

                    AssetDatabase.WriteImportSettingsIfDirty(item.path);
                    AssetDatabase.ImportAsset(item.path,ImportAssetOptions.ForceUpdate);
                }
            } finally {AssetDatabase.StopAssetEditing();}
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            foreach(var item in batch) {
                var sprite=AssetDatabase.LoadAssetAtPath<Sprite>(item.path);
                if(sprite==null)throw new InvalidOperationException("Sprite import failed: "+item.path);
                sprites.Add(item.id,sprite);
            }
            NativeCheckpoint("textures",Math.Min(start+batchSize,plan.textures.Length),plan.textures.Length);
        }
        return sprites;
    }

    const string bitmap="Assets/TextMesh Pro/Shaders/TMP_Bitmap-Custom-Atlas.shader";
    const string distance="Assets/TextMesh Pro/Shaders/TMP_SDF.shader";
    const string mobile="Assets/TextMesh Pro/Shaders/TMP_SDF-Mobile.shader";
    const string settings="Assets/TextMesh Pro/Resources/TMP Settings.asset";
    static bool NeedsTmp(Plan plan) {return plan.bitmapFonts.Length>0 || plan.assets.Any(a=>a.path.EndsWith(".ttf",StringComparison.OrdinalIgnoreCase));}
    static bool TmpFilesPresent() {return File.Exists(bitmap) && File.Exists(distance) && File.Exists(mobile) && File.Exists(settings);}
    static string ResolveTmpArchive(TmpResourceSpec spec) {
        if(spec==null || spec.importMode!="package-completion-callback" || spec.packageName!="com.unity.ugui" || spec.packageVersion!="2.6.0" || spec.resource!="Package Resources/TMP Essential Resources.unitypackage")
            throw new InvalidOperationException("TMP_RESOURCE_CONTRACT_MISMATCH: regenerate the supported candidate");
        var package=UnityEditor.PackageManager.PackageInfo.FindForAssetPath("Packages/com.unity.ugui/package.json");
        if(package==null || string.IsNullOrEmpty(package.resolvedPath))
            throw new InvalidOperationException("TMP_PACKAGE_UNRESOLVED: com.unity.ugui");
        if(package.name!=spec.packageName || package.version!=spec.packageVersion)
            throw new InvalidOperationException("TMP_PACKAGE_VERSION_MISMATCH: "+package.name+" "+package.version);
        var archive=Path.Combine(package.resolvedPath,spec.resource);
        if(!File.Exists(archive))throw new InvalidOperationException("TMP_ESSENTIAL_ARCHIVE_MISSING: "+spec.resource);
        tmpResourceResult=new TmpResourceResult {status="resolved",packageName=package.name,packageVersion=package.version,
            source=package.source.ToString(),resource=spec.resource,archiveSha256=Hash(archive),completionProof=tmpImportCompleted?"package-completed-event":"preexisting-files"};
        WriteTmpResourceResult();

        return archive;
    }
    static void EnsureTmpResources(TmpResourceSpec spec) {
        NativeCheckpoint("tmp-resources",0,1);ResolveTmpArchive(spec);
        if(!TmpFilesPresent()) {
            tmpResourceResult.status=asyncRunning?"import_incomplete":"async_entrypoint_required";WriteTmpResourceResult();
            throw new InvalidOperationException(asyncRunning?"TMP_ESSENTIAL_IMPORT_INCOMPLETE: completion event received but required files are absent":"TMP_RESOURCES_REQUIRE_ASYNC_ENTRYPOINT: use monkey native-import; unity run always adds -quit");
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        tmpBitmapShader=AssetDatabase.LoadAssetAtPath<Shader>(bitmap);
        tmpDistanceShader=AssetDatabase.LoadAssetAtPath<Shader>(distance);
        var mobileShader=AssetDatabase.LoadAssetAtPath<Shader>(mobile);
        var settingsAsset=AssetDatabase.LoadAssetAtPath<TMPro.TMP_Settings>(settings);
        if(tmpBitmapShader==null || tmpDistanceShader==null || mobileShader==null || settingsAsset==null) {
            tmpResourceResult.status="assets_not_ready";WriteTmpResourceResult();
            throw new InvalidOperationException("TMP_ESSENTIAL_ASSETS_NOT_READY: required files exist but native assets did not load");
        }
        if(tmpBitmapShader.name!="TextMeshPro/Bitmap Custom Atlas" || tmpDistanceShader.name!="TextMeshPro/Distance Field" || mobileShader.name!="TextMeshPro/Mobile/Distance Field") {
            tmpResourceResult.status="shader_name_mismatch";WriteTmpResourceResult();
            throw new InvalidOperationException("TMP_SHADER_NAME_MISMATCH: no shader substitution permitted");
        }
        tmpResourceResult.bitmapGuid=AssetDatabase.AssetPathToGUID(bitmap);tmpResourceResult.distanceGuid=AssetDatabase.AssetPathToGUID(distance);
        tmpResourceResult.mobileGuid=AssetDatabase.AssetPathToGUID(mobile);tmpResourceResult.settingsGuid=AssetDatabase.AssetPathToGUID(settings);
        tmpResourceResult.status="ready";WriteTmpResourceResult();NativeCheckpoint("tmp-resources",1,1);
    }
    static void WriteTmpResourceResult() {
        Directory.CreateDirectory("Analysis");File.WriteAllText("Analysis/tmp-resources.json",JsonUtility.ToJson(tmpResourceResult,true));
    }

    static void ValidateEditorContext() {
        if (Application.unityVersion != "6000.6.2f1")
            throw new InvalidOperationException("Candidate requires Unity 6000.6.2f1; no automatic version migration");
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            throw new InvalidOperationException("Editor must be idle");
        if (File.Exists(PrefabPath) || File.Exists(ScenePath) || File.Exists(BootstrapPath))
            throw new InvalidOperationException("Create-only import: Prefab/Scene already exists. Use a new candidate.");
        for(int i=0;i<SceneManager.sceneCount;i++) {
            var open=SceneManager.GetSceneAt(i);
            if(open.isDirty)throw new InvalidOperationException("Open scene has unsaved work; import refused");
            if(string.IsNullOrEmpty(open.path) && !(Application.isBatchMode && SceneManager.sceneCount==1))
                throw new InvalidOperationException("UNTITLED_SCENE_CONTEXT: save or close the user's untitled scene before menu import");
        }
    }

    static void Run()
    {
        ValidateEditorContext();
        var plan = JsonUtility.FromJson<Plan>(File.ReadAllText("Assets/Monkey/Editor/import-plan.json"));
        var diagnostics = new List<string>();
        foreach(var directory in new[]{Path.GetDirectoryName(PrefabPath),Path.GetDirectoryName(ScenePath),"Assets/Generated/Art","Assets/Generated/Controllers","Analysis"})
            Directory.CreateDirectory(directory);
        foreach(var font in plan.bitmapFonts)Directory.CreateDirectory(Path.GetDirectoryName(font.fontPath));
        foreach(var animation in plan.animations.Where(a=>a.convertible))Directory.CreateDirectory(Path.GetDirectoryName(animation.path));
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        if (plan.sourceDiagnosticCount > 0) diagnostics.Add("SOURCE_GAPS: " + plan.sourceDiagnosticCount);
        if(NeedsTmp(plan))EnsureTmpResources(plan.tmpResources);
        var spriteMap = ImportTextures(plan);
        NativeCheckpoint("fonts",0,plan.bitmapFonts.Length+plan.assets.Count(a=>a.path.EndsWith(".ttf",StringComparison.OrdinalIgnoreCase)));
        var fonts = new Dictionary<string, TMPro.TMP_FontAsset>();
        int fontProgress=0;int fontTotal=plan.bitmapFonts.Length+plan.assets.Count(a=>a.path.EndsWith(".ttf",StringComparison.OrdinalIgnoreCase));
        foreach (var item in plan.assets.Where(a => a.path.EndsWith(".ttf", StringComparison.OrdinalIgnoreCase)))
        {
            NativeCheckpoint("fonts",fontProgress++,fontTotal);
            var source = AssetDatabase.LoadAssetAtPath<Font>(item.path);
            if (source == null) { diagnostics.Add("FONT_IMPORT_FAILED: " + item.id); continue; }
            if (tmpDistanceShader == null) {
                diagnostics.Add("TMP_SHADER_RESOURCES_MISSING: " + item.id); continue;
            }
            var font = TMPro.TMP_FontAsset.CreateFontAsset(source,90,16,UnityEngine.TextCore.LowLevel.GlyphRenderMode.SDFAA,1024,1024,TMPro.AtlasPopulationMode.Dynamic,false);
            CheckEngineErrors();
            if (font == null) { diagnostics.Add("TMP_FONT_CREATION_FAILED: " + item.id); continue; }
            var needed = string.Concat(plan.components.Where(c=>c.type=="cc.Label" && c.convertible && c.font==item.id).Select(c=>c.text));
            // An unused original font has no requested glyphs. TMP returns false for
            // an empty request; retain a native dynamic asset backed by that source.
            if (!string.IsNullOrEmpty(needed) && !font.TryAddCharacters(needed,out string missing)) {diagnostics.Add("TTF_GLYPHS_MISSING: " + missing);UnityEngine.Object.DestroyImmediate(font);continue;}
            font.atlasPopulationMode=string.IsNullOrEmpty(needed)?TMPro.AtlasPopulationMode.Dynamic:TMPro.AtlasPopulationMode.Static;
            font.fallbackFontAssetTable=new List<TMPro.TMP_FontAsset>();
            var path = !string.IsNullOrEmpty(item.fontAssetPath)?item.fontAssetPath:item.path.Substring(0,item.path.Length-4) + ".asset";
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
            NativeCheckpoint("fonts",fontProgress++,fontTotal);
            var atlasImporter = AssetImporter.GetAtPath(spec.path) as TextureImporter;
            if (atlasImporter == null) throw new InvalidOperationException("Bitmap atlas missing: " + spec.id);
            atlasImporter.textureType = TextureImporterType.Default;
            atlasImporter.textureShape = TextureImporterShape.Texture2D;
            atlasImporter.mipmapEnabled = false; atlasImporter.npotScale = TextureImporterNPOTScale.None;
            atlasImporter.textureCompression = TextureImporterCompression.Uncompressed; atlasImporter.maxTextureSize = 16384;
            atlasImporter.SaveAndReimport();
            AssetDatabase.ImportAsset(spec.path,ImportAssetOptions.ForceSynchronousImport);
            var atlas = AssetDatabase.LoadAssetAtPath<Texture2D>(spec.path);
            if(atlas==null || AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(atlas))!=spec.atlasGuid)
                throw new InvalidOperationException("Original bitmap atlas did not import: "+spec.id+" expected="+spec.atlasGuid+" file="+AssetDatabase.AssetPathToGUID(spec.path)+" type="+AssetDatabase.GetMainAssetTypeAtPath(spec.path));
            var shader = tmpBitmapShader;
            if (shader == null) throw new InvalidOperationException("Native TMP bitmap shader unavailable after resource import");
            var font = ScriptableObject.CreateInstance<TMPro.TMP_FontAsset>();
            // Custom Atlas shader samples RGBA, retaining the source font's colored outline.
            var material = new Material(shader); material.name=Path.GetFileNameWithoutExtension(spec.fontPath)+" Material";
            material.mainTexture=atlas; material.SetColor("_FaceColor",Color.white);
            font.name = Path.GetFileNameWithoutExtension(spec.fontPath);
            font.faceInfo = new UnityEngine.TextCore.FaceInfo {
                familyName=font.name,styleName="Original",pointSize=(int)spec.pointSize,scale=1,
                lineHeight=spec.lineHeight,ascentLine=spec.ascent,descentLine=spec.descent,
                capLine=spec.ascent,meanLine=spec.ascent*.5f,baseline=0
            };
            font.atlasPopulationMode = TMPro.AtlasPopulationMode.Static;
            font.atlasTextures = new[] { atlas };
            font.fallbackFontAssetTable = new List<TMPro.TMP_FontAsset>();

            var serialized = new SerializedObject(font);
            serialized.FindProperty("m_Version").stringValue = "1.1.0";
            serialized.FindProperty("m_Material").objectReferenceValue=material;
            var atlasReferences=serialized.FindProperty("m_AtlasTextures");atlasReferences.arraySize=1;
            atlasReferences.GetArrayElementAtIndex(0).objectReferenceValue=atlas;
            serialized.FindProperty("m_AtlasWidth").intValue = spec.atlasSize[0];
            serialized.FindProperty("m_AtlasHeight").intValue = spec.atlasSize[1];
            serialized.FindProperty("m_AtlasPadding").intValue = 0;
            serialized.FindProperty("m_AtlasRenderMode").intValue=(int)UnityEngine.TextCore.LowLevel.GlyphRenderMode.RASTER;
            serialized.ApplyModifiedPropertiesWithoutUndo();CheckEngineErrors();
            font.atlasTextures=new[]{atlas};font.material=material;material.SetTexture("_MainTex",atlas);
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
            AssetDatabase.CreateAsset(font,spec.fontPath);AssetDatabase.AddObjectToAsset(material,font);
            font.ReadFontAssetDefinition();EditorUtility.SetDirty(material);EditorUtility.SetDirty(font);AssetDatabase.SaveAssetIfDirty(font);
            AssetDatabase.ImportAsset(spec.fontPath,ImportAssetOptions.ForceSynchronousImport);
            var persisted=AssetDatabase.LoadAssetAtPath<TMPro.TMP_FontAsset>(spec.fontPath);
            if(persisted==null || persisted.atlasTextures.Length!=1 || persisted.atlasTextures[0]==null || persisted.material==null || persisted.material.mainTexture==null ||
                AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(persisted.atlasTextures[0]))!=spec.atlasGuid ||
                AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(persisted.material.mainTexture))!=spec.atlasGuid)
                throw new InvalidOperationException("Saved bitmap atlas/material binding differs: "+spec.id);
            fonts[spec.id]=persisted;
        }
        // Additive preview scene preserves any previously open scene.
        NativeCheckpoint("hierarchy",0,plan.nodes.Length);
        var previous = SceneManager.GetActiveScene();priorScene=previous;
        bool ownedBatchUntitled=Application.isBatchMode && SceneManager.sceneCount==1 && string.IsNullOrEmpty(previous.path) && !previous.isDirty;
        // Only replace the clean startup scene of our dedicated batch process. Never save a user's scene.
        if(ownedBatchUntitled) {previous=default(Scene);priorScene=default(Scene);}
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,ownedBatchUntitled?NewSceneMode.Single:NewSceneMode.Additive);ownedScene=scene;
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
        var nodeSpecs = plan.nodes.ToDictionary(n=>n.sourceId);
        foreach (var node in plan.nodes)
        {
            var go = nodeMap[node.sourceId];
            var parent = node.parent != null && nodeMap.ContainsKey(node.parent) ? nodeMap[node.parent].transform : designRoot.transform;
            var rect = (RectTransform)go.transform;
            rect.SetParent(parent,false);
            var pr = parent as RectTransform;
            // Parent source data is authoritative even when that node is configured later.
            rect.anchorMin = rect.anchorMax = !string.IsNullOrEmpty(node.parent) && nodeSpecs.ContainsKey(node.parent)?
                new Vector2(nodeSpecs[node.parent].anchor[0],nodeSpecs[node.parent].anchor[1]):pr != null ? pr.pivot : Vector2.zero;
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
        int componentProgress=0;
        foreach (var spec in plan.components)
        {
            if(componentProgress++%128==0)NativeCheckpoint("components",componentProgress-1,plan.components.Length);
            if (!spec.convertible || !nodeMap.ContainsKey(spec.node)) {
                diagnostics.Add("COMPONENT_NOT_IMPORTED: " + spec.sourceId + " " + spec.type); continue;
            }
            var go = nodeMap[spec.node]; var node = nodeSpecs[spec.node];
            var color = new Color(node.color[0]/255f,node.color[1]/255f,node.color[2]/255f,node.color[3]/255f);
            if (spec.type == "cc.Sprite")
            {
                var key = spec.spriteFrame + (spec.trim ? "" : "@original");
                if (!string.IsNullOrEmpty(spec.spriteFrame) && !spriteMap.ContainsKey(key)) { diagnostics.Add("SPRITE_MISSING: " + spec.sourceId); continue; }
                if (go.GetComponent<UnityEngine.UI.Graphic>() != null) {
                    diagnostics.Add("MULTIPLE_GRAPHICS_ON_NODE: " + spec.sourceId); continue;
                }
                var image = go.AddComponent<UnityEngine.UI.Image>();
                image.sprite = string.IsNullOrEmpty(spec.spriteFrame)?null:spriteMap[key]; image.color = color; image.raycastTarget = false;
                image.type = spec.mode == 1 ? UnityEngine.UI.Image.Type.Sliced : spec.mode==2 ? UnityEngine.UI.Image.Type.Tiled : UnityEngine.UI.Image.Type.Simple;
                image.enabled = spec.enabled && !string.IsNullOrEmpty(spec.spriteFrame);
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
            if(spec.type=="cc.Widget" && spec.enabled && spec.flags==45) {
                rect.anchorMin=Vector2.zero;rect.anchorMax=Vector2.one;
                rect.offsetMin=new Vector2(spec.margins[0],spec.margins[1]);
                rect.offsetMax=new Vector2(-spec.margins[2],-spec.margins[3]);
            }
            else if(spec.type=="cc.Mask") {
                var mask=go.AddComponent<UnityEngine.UI.RectMask2D>();mask.enabled=spec.enabled;
            }
            else if(spec.type=="cc.Layout") {
                if(go.GetComponent<UnityEngine.UI.LayoutGroup>()!=null || go.GetComponent<UnityEngine.UI.ContentSizeFitter>()!=null)
                    throw new InvalidOperationException("Native layout conflict: "+spec.sourceId);
                var padding=new RectOffset((int)spec.padding[0],(int)spec.padding[2],(int)spec.padding[3],(int)spec.padding[1]);
                var fitter=go.AddComponent<UnityEngine.UI.ContentSizeFitter>();
                if(spec.layoutType==3) {
                    var group=go.AddComponent<IntrinsicGridLayoutGroup>();group.enabled=spec.enabled;
                    group.cellSize=new Vector2(spec.effectiveCellSize[0],spec.effectiveCellSize[1]);
                    group.spacing=new Vector2(spec.spacingXY[0],spec.spacingXY[1]);group.padding=padding;
                    group.startAxis=UnityEngine.UI.GridLayoutGroup.Axis.Horizontal;
                    group.startCorner=spec.verticalDirection==1?(spec.horizontalDirection==0?UnityEngine.UI.GridLayoutGroup.Corner.UpperLeft:UnityEngine.UI.GridLayoutGroup.Corner.UpperRight):
                        (spec.horizontalDirection==0?UnityEngine.UI.GridLayoutGroup.Corner.LowerLeft:UnityEngine.UI.GridLayoutGroup.Corner.LowerRight);
                    group.childAlignment=spec.verticalDirection==1?(spec.horizontalDirection==0?TextAnchor.UpperLeft:TextAnchor.UpperRight):
                        (spec.horizontalDirection==0?TextAnchor.LowerLeft:TextAnchor.LowerRight);
                    group.constraint=UnityEngine.UI.GridLayoutGroup.Constraint.Flexible;
                    fitter.verticalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
                }
                else {
                    UnityEngine.UI.HorizontalOrVerticalLayoutGroup group=spec.layoutType==1?
                        (UnityEngine.UI.HorizontalOrVerticalLayoutGroup)go.AddComponent<UnityEngine.UI.HorizontalLayoutGroup>():go.AddComponent<UnityEngine.UI.VerticalLayoutGroup>();
                    group.enabled=spec.enabled;group.padding=padding;
                    group.childControlWidth=false;group.childControlHeight=false;
                    group.childForceExpandWidth=false;group.childForceExpandHeight=false;
                    if(spec.layoutType==1) {
                        group.childScaleHeight=spec.crossAxisScale;
                        group.childAlignment=spec.crossAxisAlignment==0?TextAnchor.LowerCenter:spec.crossAxisAlignment==1?TextAnchor.UpperCenter:TextAnchor.MiddleCenter;
                    } else {
                        group.childScaleWidth=spec.crossAxisScale;
                        group.childAlignment=spec.crossAxisAlignment==0?TextAnchor.MiddleLeft:spec.crossAxisAlignment==1?TextAnchor.MiddleRight:TextAnchor.MiddleCenter;
                    }
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
        SettleNativeLayout(canvas);
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
        NativeCheckpoint("animations",0,plan.animations.Length);
        var motionReadback=BuildMotions(plan,nodeMap);
        var view = canvas.AddComponent<MonkeyCandidateView>();
        view.Images = canvas.GetComponentsInChildren<UnityEngine.UI.Image>(true);
        view.Labels = canvas.GetComponentsInChildren<TMPro.TextMeshProUGUI>(true);
        view.Buttons = canvas.GetComponentsInChildren<UnityEngine.UI.Button>(true);
        var events=new GameObject("EventSystem",typeof(UnityEngine.EventSystems.EventSystem),typeof(UnityEngine.EventSystems.StandaloneInputModule));
        SceneManager.MoveGameObjectToScene(events,scene);
        var sourcePrefabResults=new List<SourcePrefabResult>();
        foreach(var spec in plan.sourcePrefabs ?? new SourcePrefabSpec[0]) {
            if(string.IsNullOrEmpty(spec.path) || !spec.path.StartsWith("Assets/Generated/Views/Sources/",StringComparison.Ordinal) || spec.path.Contains(".."))
                throw new InvalidOperationException("Invalid source prefab path");
            Directory.CreateDirectory(Path.GetDirectoryName(spec.path));
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        foreach(var spec in plan.sourcePrefabs ?? new SourcePrefabSpec[0]) {
            if(sourcePrefabResults.Count%16==0)NativeCheckpoint("source-prefabs",sourcePrefabResults.Count,plan.sourcePrefabs.Length);
            if(!spec.path.StartsWith("Assets/Generated/Views/Sources/",StringComparison.Ordinal) || spec.path.Contains("..") || File.Exists(spec.path))
                throw new InvalidOperationException("Invalid or existing source prefab path: "+spec.path);
            // SaveAsPrefabAsset serializes this subtree without modifying it.
            // A managed active Instantiate can run layout lifecycle callbacks
            // while the cloned hierarchy is still initializing.
            var sourcePrefab=PrefabUtility.SaveAsPrefabAsset(nodeMap[spec.root],spec.path,out bool saved);
            if(!saved || sourcePrefab==null)throw new InvalidOperationException("Source prefab save failed: "+spec.sourceId);
            var contents=PrefabUtility.LoadPrefabContents(spec.path);
            try {
                int passes=SettleNativeLayout(contents);
                var transforms=contents.GetComponentsInChildren<Transform>(true);
                int missing=transforms.Sum(t=>GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
                if(transforms.Length!=spec.nodeCount || missing!=0)throw new InvalidOperationException("Source prefab reopen mismatch: "+spec.sourceId);
                var mapped=SavedNodeMap(plan.nodes,contents,spec,nodeSpecs);
                var referenceFailures=new List<string>();
                foreach(var c in plan.components.Where(c=>c.convertible&&mapped.ContainsKey(c.node))) {
                    var go=mapped[c.node].gameObject;bool valid=true;
                    if(c.type=="cc.Sprite") {
                        var image=go.GetComponent<UnityEngine.UI.Image>();
                        valid=image!=null && (string.IsNullOrEmpty(c.spriteFrame)?image.sprite==null:image.sprite==spriteMap[c.spriteFrame+(c.trim?"":"@original")]);
                    } else if(c.type=="cc.Label" || c.type=="cc.LabelOutline") {
                        var label=go.GetComponent<TMPro.TextMeshProUGUI>();
                        valid=label!=null && (c.type=="cc.LabelOutline" || (label.font==fonts[c.font]&&label.text==c.text));
                    } else if(c.type=="cc.Button") {
                        var button=go.GetComponent<UnityEngine.UI.Button>();valid=button!=null&&button.targetGraphic==go.GetComponent<UnityEngine.UI.Graphic>();
                    } else if(c.type=="cc.ScrollView") {
                        var scroll=go.GetComponent<UnityEngine.UI.ScrollRect>();valid=scroll!=null&&mapped.ContainsKey(c.content)&&scroll.content==mapped[c.content];
                    } else if(c.type=="cc.Mask")valid=go.GetComponent<UnityEngine.UI.RectMask2D>()!=null;
                    else if(c.type=="cc.Layout")valid=go.GetComponent<UnityEngine.UI.LayoutGroup>()!=null;
                    if(!valid)referenceFailures.Add(c.sourceId);
                }
                sourcePrefabResults.Add(new SourcePrefabResult {sourceId=spec.sourceId,path=spec.path,
                    guid=AssetDatabase.AssetPathToGUID(spec.path),nodeCount=transforms.Length,missingScripts=missing,
                    savedReloaded=true,geometryPhase="native-layout-settled-v1",layoutSettlePasses=passes,
                    nodes=spec.nodes.Select(id=>DescribeNode(nodeSpecs[id],mapped[id])).ToArray(),
                    referencesVerified=referenceFailures.Count==0,referenceFailures=referenceFailures.ToArray()});
            } finally { PrefabUtility.UnloadPrefabContents(contents); }
        }
        NativeCheckpoint("candidate-save",0,1);
        var prefab = PrefabUtility.SaveAsPrefabAsset(canvas,PrefabPath,out var success);
        if (!success || prefab == null) throw new InvalidOperationException("Native Prefab save failed");
        UnityEngine.Object.DestroyImmediate(canvas);
        var instance=(GameObject)PrefabUtility.InstantiatePrefab(prefab,scene);
        if (!EditorSceneManager.SaveScene(scene,ScenePath)) throw new InvalidOperationException("Native scene save failed");
        NativeCheckpoint("scene-reopen",0,1);
        if(ownedBatchUntitled) {
            // Opening the saved scene in Single mode normally closes/reloads the only owned scene.
            scene=EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Single);
        } else {
            if(!EditorSceneManager.CloseScene(scene,true))throw new InvalidOperationException("Owned scene close failed");
            scene=EditorSceneManager.OpenScene(ScenePath,OpenSceneMode.Additive);
        }
        ownedScene=scene;
        if(!scene.IsValid() || !scene.isLoaded)throw new InvalidOperationException("Saved scene reopen failed");
        instance=scene.GetRootGameObjects().FirstOrDefault(go=>go.GetComponent<MonkeyCandidateView>()!=null);
        if(instance==null)throw new InvalidOperationException("Reopened scene has no serialized candidate view");
        SettleNativeLayout(instance);
        if(!EditorSceneManager.SaveScene(scene,ScenePath))throw new InvalidOperationException("Settled native scene save failed");
        NativeCheckpoint("scene-reopen",1,1);
        NativeCheckpoint("native-readback",0,1);
        var savedNodeMap=SavedNodeMap(plan.nodes,instance);
        var readback = new Readback {
            sourcePrefabs=sourcePrefabResults.ToArray(),tmpResources=tmpResourceResult,sceneReopened=true,
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
                // Resolve the reloaded scene once by sibling-index paths, independent of names.
                var target=savedNodeMap[n.sourceId];
                return DescribeNode(n,target);
            }).ToArray(),
            fonts=fonts.Select(pair=>new FontResult { id=pair.Key,guid=AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(pair.Value)),
                atlasGuid=pair.Value.atlasTextures.Length>0 && pair.Value.atlasTextures[0]!=null?AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(pair.Value.atlasTextures[0])):"",
                materialAtlasGuid=pair.Value.material!=null && pair.Value.material.mainTexture!=null?AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(pair.Value.material.mainTexture)):"",
                glyphCount=pair.Value.glyphTable.Count,characterCount=pair.Value.characterTable.Count,
                pointSize=pair.Value.faceInfo.pointSize,lineHeight=pair.Value.faceInfo.lineHeight }).ToArray(),
            labels=plan.components.Where(c=>c.convertible && c.type=="cc.Label").Select(c=>
                ReadSavedLabel(c,savedNodeMap[c.node],plan.bitmapFonts.Any(f=>f.id==c.font))).ToArray(),
            sprites=plan.textures.Select(t=>{
                var s=spriteMap[t.id];AssetDatabase.TryGetGUIDAndLocalFileIdentifier(s,out string g,out long id);
                return new SpriteResult {id=t.id,guid=g,fileId=id,size=new[]{s.rect.width,s.rect.height},
                    border=new[]{s.border.x,s.border.y,s.border.z,s.border.w}};
            }).ToArray()
        };
        var savedView=instance.GetComponent<MonkeyCandidateView>();
        readback.viewReferences=plan.components.Where(c=>c.convertible && new[]{"cc.Sprite","cc.Label","cc.Button"}.Contains(c.type)).Select(c=> {
            var node=savedNodeMap[c.node];
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
        nativeProgress.phase="complete";nativeProgress.processed=1;nativeProgress.total=1;WriteNativeProgress(readback.status=="imported"?"completed":"completed_partial");
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
    static NodeResult DescribeNode(NodeSpec source,RectTransform rect) {
        return new NodeResult {sourceId=source.sourceId,hierarchy=rect.name,size=new[]{rect.rect.width,rect.rect.height},
            pivot=new[]{rect.pivot.x,rect.pivot.y},position=new[]{rect.localPosition.x,rect.localPosition.y,rect.localPosition.z},
            scale=new[]{rect.localScale.x,rect.localScale.y,rect.localScale.z},
            rotation=new[]{rect.localRotation.x,rect.localRotation.y,rect.localRotation.z,rect.localRotation.w},
            active=rect.gameObject.activeSelf,componentTypes=rect.GetComponents<Component>().Select(c=>c.GetType().FullName).ToArray()};
    }
    static int SettleNativeLayout(GameObject root) {
        var groups=root.GetComponentsInChildren<UnityEngine.UI.LayoutGroup>(true).Where(g=>g.isActiveAndEnabled).Reverse().ToArray();
        if(groups.Length==0)return 0;
        var rects=root.GetComponentsInChildren<RectTransform>(true);
        Func<RectTransform,Vector4> value=r=>new Vector4(r.rect.width,r.rect.height,r.localPosition.x,r.localPosition.y);
        for(int pass=0;pass<8;pass++) {
            NativeCheckpoint(nativeProgress.phase,nativeProgress.processed,nativeProgress.total);
            var before=rects.Select(value).ToArray();
            // DesignRoot is not an ILayoutController: forcing only that root is
            // a no-op. Resolve actual native groups, children before parents.
            foreach(var group in groups)UnityEngine.UI.LayoutRebuilder.ForceRebuildLayoutImmediate((RectTransform)group.transform);
            Canvas.ForceUpdateCanvases();
            if(rects.Select((r,i)=>(value(r)-before[i]).sqrMagnitude).All(d=>d<1e-10f))return pass+1;
        }
        throw new InvalidOperationException("NATIVE_LAYOUT_DID_NOT_SETTLE");
    }
    static Dictionary<string,RectTransform> SavedNodeMap(NodeSpec[] nodes,GameObject instance,SourcePrefabSpec prefab=null,Dictionary<string,NodeSpec> byId=null) {
        byId=byId??nodes.ToDictionary(n=>n.sourceId);
        var mapped=new Dictionary<string,RectTransform>();
        var pending=new Stack<KeyValuePair<NodeSpec,Transform>>();
        if(prefab!=null)pending.Push(new KeyValuePair<NodeSpec,Transform>(byId[prefab.root],instance.transform));
        else {
            var roots=nodes.Where(n=>string.IsNullOrEmpty(n.parent) || !byId.ContainsKey(n.parent)).ToArray();
            var design=instance.transform.Find("DesignRoot");
            if(design==null || design.childCount!=roots.Length)throw new InvalidOperationException("Saved source root boundary differs");
            for(int i=roots.Length-1;i>=0;i--)pending.Push(new KeyValuePair<NodeSpec,Transform>(roots[i],design.GetChild(i)));
        }
        while(pending.Count>0) {
            var pair=pending.Pop();var source=pair.Key;var target=pair.Value as RectTransform;
            if(target==null || target.childCount<source.children.Length)throw new InvalidOperationException("Saved source node boundary differs: "+source.sourceId);
            mapped.Add(source.sourceId,target);
            for(int i=source.children.Length-1;i>=0;i--)pending.Push(new KeyValuePair<NodeSpec,Transform>(byId[source.children[i]],target.GetChild(i)));
        }
        if(mapped.Count!=(prefab==null?nodes.Length:prefab.nodeCount))throw new InvalidOperationException("Saved source node count differs");
        return mapped;
    }
    static LabelResult ReadSavedLabel(ComponentSpec spec,RectTransform saved,bool bitmap) {
        var label=saved.GetComponent<TMPro.TextMeshProUGUI>();
        if(label==null)return new LabelResult {sourceId=spec.sourceId,allCharactersPresent=false};
        GameObject probeCanvas=null;var measured=label;string geometryProbe="saved-node";
        try {
            label.ForceMeshUpdate(true,true);
            if(!label.gameObject.activeInHierarchy || !label.enabled || (!string.IsNullOrEmpty(label.text) && label.textInfo.characterCount==0)) {
                // An active clone measures hidden text without activating or changing the saved scene tree.
                probeCanvas=new GameObject("MonkeyTextGeometryProbe",typeof(RectTransform),typeof(Canvas));
                SceneManager.MoveGameObjectToScene(probeCanvas,label.gameObject.scene);
                probeCanvas.GetComponent<Canvas>().renderMode=RenderMode.WorldSpace;
                var clone=UnityEngine.Object.Instantiate(label.gameObject,probeCanvas.transform,false);
                measured=clone.GetComponent<TMPro.TextMeshProUGUI>();
                foreach(var behaviour in clone.GetComponentsInChildren<Behaviour>(true))if(behaviour!=measured)behaviour.enabled=false;
                var rect=(RectTransform)clone.transform;rect.anchorMin=rect.anchorMax=new Vector2(.5f,.5f);
                rect.pivot=saved.pivot;rect.sizeDelta=saved.rect.size;rect.anchoredPosition3D=Vector3.zero;
                clone.SetActive(true);measured.enabled=true;geometryProbe="isolated-active-clone";
                measured.ForceMeshUpdate(true,true);
            }
            float padding=bitmap?TMPro.ShaderUtilities.GetPadding(measured.fontSharedMaterial,measured.extraPadding,(measured.fontStyle&TMPro.FontStyles.Bold)!=0):0;
            return new LabelResult {sourceId=spec.sourceId,text=measured.text,fontGuid=AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(measured.font)),
                fontSize=measured.fontSize,characterCount=measured.textInfo.characterCount,geometryProbe=geometryProbe,
                glyphBounds=measured.textInfo.characterInfo.Take(measured.textInfo.characterCount).Where(info=>info.isVisible).Select(info=>new GlyphBounds {
                    unicode=info.character,left=info.bottomLeft.x,top=info.topLeft.y,width=info.topRight.x-info.topLeft.x,height=info.topLeft.y-info.bottomLeft.y,
                    quadPadding=padding*info.scale
                }).ToArray(),allCharactersPresent=measured.text.Where(ch=>!char.IsWhiteSpace(ch)).All(ch=>measured.font.HasCharacter(ch))};
        } finally {if(probeCanvas!=null)UnityEngine.Object.DestroyImmediate(probeCanvas);}
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
