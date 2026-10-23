using UnityEngine;
using UnityEngine.UI;

// Keep uGUI's own width-dependent row calculation. A Graphic on the same
// object must not replace the grid's content metrics with its texture size.
[AddComponentMenu("Layout/Intrinsic Grid Layout Group")]
public sealed class IntrinsicGridLayoutGroup : GridLayoutGroup
{
    public override int layoutPriority { get { return 1; } }
}
