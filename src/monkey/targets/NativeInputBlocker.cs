using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

// A bounded native UI event sink. It never invokes recovered business events.
[DisallowMultipleComponent]
public sealed class NativeInputBlocker : MonoBehaviour,
    IPointerDownHandler, IPointerUpHandler, IPointerClickHandler,
    IPointerEnterHandler, IPointerExitHandler, IScrollHandler,
    IBeginDragHandler, IDragHandler, IEndDragHandler
{
    [SerializeField] private Graphic surface;
    [SerializeField] private bool previousRaycast;
    [SerializeField] private bool ownsSurface;
    public Graphic Surface => surface;

    public void Configure(Graphic existing)
    {
        surface = existing;
        if (surface == null) {
            surface = gameObject.AddComponent<NativeInputBlockerSurface>();
            ownsSurface = true;
        }
        previousRaycast = surface.raycastTarget;
        Apply(isActiveAndEnabled);
    }
    void OnEnable() { Apply(true); }
    void OnDisable() { Apply(false); }
    void Apply(bool active) {
        if (surface == null) return;
        surface.raycastTarget = active || (!ownsSurface && previousRaycast);
        if (ownsSurface) surface.enabled = active;
    }
    public void OnPointerDown(PointerEventData e) { e.Use(); }
    public void OnPointerUp(PointerEventData e) { e.Use(); }
    public void OnPointerClick(PointerEventData e) { e.Use(); }
    public void OnPointerEnter(PointerEventData e) { e.Use(); }
    public void OnPointerExit(PointerEventData e) { e.Use(); }
    public void OnScroll(PointerEventData e) { e.Use(); }
    public void OnBeginDrag(PointerEventData e) { e.Use(); }
    public void OnDrag(PointerEventData e) { e.Use(); }
    public void OnEndDrag(PointerEventData e) { e.Use(); }
}
