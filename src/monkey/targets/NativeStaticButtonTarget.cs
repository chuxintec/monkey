using UnityEngine;

// Explicit native reference retained when a source Button targets a grouping
// node without a Graphic. This component has no callbacks or runtime behavior.
public sealed class NativeStaticButtonTarget : MonoBehaviour
{
    public GameObject Target;
    public bool SourceEnabled;
}
