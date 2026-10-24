using System;
using System.Linq;
using UnityEngine;

public static partial class MonkeyImporter
{
    static GameObject CreatePrefabUiContext(GameObject contents,Plan plan) {
        var context=new GameObject("OwnedPrefabUiContext",typeof(RectTransform),typeof(Canvas));
        UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(context,contents.scene);
        context.GetComponent<Canvas>().renderMode=RenderMode.WorldSpace;
        var rect=(RectTransform)context.transform;rect.pivot=Vector2.zero;rect.sizeDelta=new Vector2(plan.designSize[0],plan.designSize[1]);
        contents.transform.SetParent(rect,false);
        return context;
    }
    [Serializable] public class DynamicUiState { public string action;public float[] size,position;public float fontSize; }
    [Serializable] public class DynamicUiResult { public string sourceId,type,status;public DynamicUiState[] states; }
    static DynamicUiState UiState(string action,RectTransform rect) {
        var label=rect.GetComponent<TMPro.TextMeshProUGUI>();
        return new DynamicUiState {action=action,size=new[]{rect.rect.width,rect.rect.height},position=new[]{rect.localPosition.x,rect.localPosition.y},fontSize=label!=null?label.fontSize:0};
    }
    static DynamicUiResult[] ProbeDynamicUi(Plan plan,GameObject instance) {
        var results=new System.Collections.Generic.List<DynamicUiResult>();
        var selected=plan.components.Where(c=>c.convertible&&c.enabled&&
            ((c.type=="cc.Label"&&!string.IsNullOrEmpty(c.text))||c.type=="cc.Widget"||c.type=="cc.Layout"&&(c.layoutType==1||c.layoutType==2)&&c.resize==1))
            .GroupBy(c=>c.type=="cc.Label"?c.type+"/"+c.overflow:c.type).Select(g=>g.First()).Take(6);
        foreach(var spec in selected) {
            var clone=UnityEngine.Object.Instantiate(instance);clone.name="OwnedDynamicUiProbe";
            try {
                var mapped=SavedNodeMap(plan.nodes,clone);var rect=mapped[spec.node];
                for(var p=rect.transform;p!=null;p=p.parent)p.gameObject.SetActive(true);
                SettleNativeLayout(clone);var states=new System.Collections.Generic.List<DynamicUiState>{UiState("baseline",rect)};
                if(spec.type=="cc.Label") {
                    var label=rect.GetComponent<TMPro.TextMeshProUGUI>();var original=label.text;
                    label.text=spec.overflow==3?original+"\n"+original:original+original;
                    SettleNativeLayout(clone);states.Add(UiState("text-change",rect));
                    if(spec.overflow==0&&rect.rect.width+0.01f<states[0].size[0]||spec.overflow==3&&rect.rect.height+0.01f<states[0].size[1])throw new InvalidOperationException("Native text sizing did not grow");
                    var grown=rect.rect.size;rect.gameObject.SetActive(false);label.text=original;
                    rect.gameObject.SetActive(true);SettleNativeLayout(clone);states.Add(UiState("show-original-text",rect));
                    if((rect.rect.size-new Vector2(states[0].size[0],states[0].size[1])).sqrMagnitude>.01f)throw new InvalidOperationException("Text hidden/restore geometry differs");
                } else if(spec.type=="cc.Widget") {
                    var constraint=rect.GetComponent<NativeRectConstraints>();var parent=rect.parent as RectTransform;
                    if(constraint==null||parent==null)continue;
                    var size=parent.rect.size;parent.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,size.x+40);parent.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,size.y+20);
                    SettleNativeLayout(clone);states.Add(UiState("parent-resize",rect));
                    rect.gameObject.SetActive(false);parent.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,size.x+80);
                    rect.gameObject.SetActive(true);SettleNativeLayout(clone);states.Add(UiState("show-after-resize",rect));
                } else {
                    var group=rect.GetComponent<NativeLinearLayoutGroup>();if(group==null)continue;
                    var child=new GameObject("OwnedDynamicChild",typeof(RectTransform));var added=(RectTransform)child.transform;
                    added.SetParent(rect,false);added.sizeDelta=new Vector2(40,20);
                    SettleNativeLayout(clone);states.Add(UiState("add-child",rect));
                    float expected=states[0].size[group.Axis]+(group.Axis==0?40:20)+group.Spacing;
                    if(Math.Abs(rect.rect.size[group.Axis]-expected)>.01f)throw new InvalidOperationException("Dynamic child layout extent differs");
                    child.SetActive(false);SettleNativeLayout(clone);states.Add(UiState("hide-child",rect));
                    child.SetActive(true);SettleNativeLayout(clone);states.Add(UiState("show-child",rect));
                    UnityEngine.Object.DestroyImmediate(child);SettleNativeLayout(clone);states.Add(UiState("remove-child",rect));
                    if(Math.Abs(rect.rect.size[group.Axis]-states[0].size[group.Axis])>.01f)throw new InvalidOperationException("Dynamic child removal did not restore extent");
                }
                results.Add(new DynamicUiResult{sourceId=spec.sourceId,type=spec.type,status="native-state-changes-passed",states=states.ToArray()});
            } finally {UnityEngine.Object.DestroyImmediate(clone);}
        }
        return results.ToArray();
    }
    static void ConfigureWidget(GameObject go,ComponentSpec spec) {
        var controller=go.AddComponent<NativeRectConstraints>();controller.enabled=false;
        Func<int,int,int,NativeRectConstraints.Edge> edge=(min,center,max)=>
            (spec.flags&min)!=0&&(spec.flags&max)!=0?NativeRectConstraints.Edge.Stretch:
            (spec.flags&min)!=0?NativeRectConstraints.Edge.Minimum:
            (spec.flags&max)!=0?NativeRectConstraints.Edge.Maximum:
            (spec.flags&center)!=0?NativeRectConstraints.Edge.Center:NativeRectConstraints.Edge.Unconstrained;
        controller.Horizontal=edge(8,16,32);controller.Vertical=edge(4,2,1);
        controller.Policy=(NativeRectConstraints.UpdatePolicy)spec.alignMode;
        var minimum=Vector2.zero;var maximum=Vector2.zero;var minimumFraction=Vector2.zero;var maximumFraction=Vector2.zero;
        for(int axis=0;axis<2;axis++) {
            if(spec.absolute[axis])minimum[axis]=spec.margins[axis];else minimumFraction[axis]=spec.margins[axis];
            if(spec.absolute[axis+2])maximum[axis]=spec.margins[axis+2];else maximumFraction[axis]=spec.margins[axis+2];
        }
        controller.Minimum=minimum;controller.Maximum=maximum;controller.MinimumFraction=minimumFraction;controller.MaximumFraction=maximumFraction;
        for(int axis=0;axis<2;axis++){if(spec.centerAbsolute[axis])controller.Center[axis]=spec.center[axis];else controller.CenterFraction[axis]=spec.center[axis];}
        controller.Configured=true;controller.enabled=spec.enabled;controller.Refresh();
    }
    static void ConfigureLabel(GameObject go,TMPro.TextMeshProUGUI label,ComponentSpec spec,bool bitmap) {
        float lineHeight=spec.lineHeight==0?spec.fontSize:spec.lineHeight;
        label.lineSpacing=spec.fontSize>0?(lineHeight-label.font.faceInfo.lineHeight*spec.fontSize/label.font.faceInfo.pointSize)*100f/spec.fontSize:0;
        label.enableAutoSizing=spec.overflow==2;label.fontSizeMax=spec.fontSize;label.fontSizeMin=.1f;
        label.overflowMode=spec.overflow==1?TMPro.TextOverflowModes.Masking:TMPro.TextOverflowModes.Overflow;
        if(spec.overflow==0||spec.overflow==3) {
            if(!bitmap){var box=go.AddComponent<NativeTextLineBox>();box.LineHeight=lineHeight;box.ExtraLineFraction=.26f;box.enabled=spec.enabled;}
            var fitter=go.AddComponent<UnityEngine.UI.ContentSizeFitter>();
            fitter.horizontalFit=spec.overflow==0?UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize:UnityEngine.UI.ContentSizeFitter.FitMode.Unconstrained;
            fitter.verticalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;fitter.enabled=spec.enabled;
        }
    }
    static void ConfigureLinearLayout(GameObject go,ComponentSpec spec) {
        var group=go.AddComponent<NativeLinearLayoutGroup>();group.enabled=false;
        group.Axis=spec.layoutType-1;group.Reverse=spec.layoutType==1?spec.horizontalDirection==1:spec.verticalDirection==1;
        group.ResizeContainer=spec.resize==1;group.IncludeScale=spec.affectedByScale;group.AlignCrossAxis=spec.alignCross;
        group.Spacing=spec.spacingXY[group.Axis];group.padding=new RectOffset((int)spec.padding[0],(int)spec.padding[2],(int)spec.padding[3],(int)spec.padding[1]);
        group.enabled=spec.enabled;
        if(spec.resize==1){var fitter=go.AddComponent<UnityEngine.UI.ContentSizeFitter>();
            if(group.Axis==0)fitter.horizontalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
            else fitter.verticalFit=UnityEngine.UI.ContentSizeFitter.FitMode.PreferredSize;
            fitter.enabled=spec.enabled;
        }
    }
}
