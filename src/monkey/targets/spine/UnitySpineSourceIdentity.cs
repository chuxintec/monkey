using UnityEngine;

// Serialized, callback-free identity metadata for source Spine components.
// It lets Editor readback distinguish multiple native renderers on one node.
[AddComponentMenu("")]
public sealed class UnitySpineSourceIdentity : MonoBehaviour
{
    [HideInInspector] public string sourceComponentId;
    [HideInInspector] public string rendererKind;
    [HideInInspector] public Behaviour renderer;
    [HideInInspector] public float sourceTimeScale;
    [HideInInspector] public float nativeTimeScale;
    [HideInInspector] public bool sourceTimeScaleVerified;
    [HideInInspector] public bool persistentVisiblePose;
}
