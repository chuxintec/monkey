import { _decorator, CCBoolean, CCInteger, Component, Label, Mask, Node, RichText, Sorting2D, Sprite, UIRenderer } from 'cc';
const { ccclass, property, executeInEditMode } = _decorator;

@ccclass('MonkeyStaticSortQueueProxyPresenter')
@executeInEditMode
export class CreatorStaticSortQueueProxyPresenter extends Component {
    private serializationPrepared = false;
    @property public sourceRootId = '';
    @property public sourcePrefabId = '';
    @property public prefabPath = '';
    @property(Node) public sourceRoot: Node | null = null;
    @property(Node) public proxyRoot: Node | null = null;
    @property([Node]) public sourceNodes: Node[] = [];
    @property([Node]) public proxyNodes: Node[] = [];
    // Renderer identity can be a UIRenderer or a native cc.RichText component
    // whose generated child Labels/Sprites carry the Sorting2D priorities.
    @property([Component]) public sourceRenderers: Component[] = [];
    @property([Component]) public proxyRenderers: Component[] = [];
    @property({ type: [CCInteger] }) public proxySortOrders: number[] = [];
    @property([Mask]) public sourceMasks: Mask[] = [];
    @property([Mask]) public proxyMasks: Mask[] = [];
    @property([Node]) public nestedProxyRoots: Node[] = [];
    @property({ type: [CCBoolean] }) public nestedProxyRootActiveBefore: boolean[] = [];
    @property public originalLayers: number[] = [];
    @property public hiddenLayer = 1 << 28;
    @property public queueSha256 = '';
    @property public sourceTreeStayedUnmodified = true;

    onLoad(): void { this.suppressSourceLayers(); }
    onEnable(): void {
        this.suppressSourceLayers();
        // RichText's native segment Nodes have DontSave hide flags. Their
        // Sorting2D components are recreated from this persistent parent
        // binding after the RichText lifecycle generates those segments.
        this.scheduleOnce(this.initializeProxyRichTextSorting, 0);
    }
    onDisable(): void {
        this.clearGeneratedRichTextSorting();
        this.restoreSourceLayers();
        // Creator serialization temporarily detaches the source Prefab root.
        // Keep inherited/template proxy roots disabled in the bytes being
        // serialized; ordinary disable/destruction still restores them.
        if (!this.serializationPrepared) this.restoreNestedProxyRoots();
    }
    onDestroy(): void { this.clearGeneratedRichTextSorting(); }

    public captureOriginalLayers(nodes: Node[]): void {
        this.sourceNodes = nodes.slice();
        this.originalLayers = nodes.map(node => node.layer);
    }

    public suppressSourceLayers(): void {
        this.disableNestedProxyRoots();
        for (const node of this.sourceNodes) if (node && node.isValid) node.layer = this.hiddenLayer;
    }

    public restoreSourceLayers(): void {
        for (let index = 0; index < this.sourceNodes.length; index++) {
            const node = this.sourceNodes[index];
            if (node && node.isValid && index < this.originalLayers.length) node.layer = this.originalLayers[index];
        }
    }

    /** Call immediately before serializing/saving the source Prefab asset. */
    public restoreAuthoredLayers(): void { this.restoreSourceLayers(); }
    public prepareForSerialization(): void {
        this.serializationPrepared = true;
        this.restoreAuthoredLayers();
        this.disableNestedProxyRoots();
    }
    public restoreAfterSerialization(): void {
        this.serializationPrepared = false;
        this.initializeEditorInstance();
    }
    public initializeEditorInstance(): void {
        this.serializationPrepared = false;
        this.suppressSourceLayers(); this.initializeProxyRichTextSorting();
    }

    private initializeProxyRichTextSorting(): void {
        if (this.proxyRenderers.length !== this.proxySortOrders.length) return;
        for (let index = 0; index < this.proxyRenderers.length; index++) {
            const richText = this.proxyRenderers[index];
            if (!(richText instanceof RichText)) continue;
            for (const child of richText.node.children) {
                if (!child.hideFlags || (child.name !== 'RICHTEXT_CHILD' && child.name !== 'RICHTEXT_Image_CHILD')) continue;
                const renderers = child.getComponents(UIRenderer);
                if (renderers.length !== 1 || (!(renderers[0] instanceof Label) && !(renderers[0] instanceof Sprite)))
                    throw new Error(`CREATOR_PROXY_RICHTEXT_SEGMENT_RENDERER_IDENTITY:${child.name}`);
                let sorting = child.getComponent(Sorting2D);
                if (!sorting) sorting = child.addComponent(Sorting2D);
                sorting.sortingOrder = this.proxySortOrders[index];
            }
        }
    }

    private clearGeneratedRichTextSorting(): void {
        for (const component of this.proxyRenderers) {
            if (!(component instanceof RichText)) continue;
            for (const child of component.node.children) {
                if (!child.hideFlags || (child.name !== 'RICHTEXT_CHILD' && child.name !== 'RICHTEXT_Image_CHILD')) continue;
                const sorting = child.getComponent(Sorting2D);
                if (sorting) child.removeComponent(sorting);
            }
        }
    }

    private disableNestedProxyRoots(): void {
        for (const root of this.nestedProxyRoots.slice().sort((a, b) => this.depth(a) - this.depth(b)))
            if (root && root.isValid && root.active) root.active = false;
    }

    private restoreNestedProxyRoots(): void {
        const indexes = this.nestedProxyRoots.map((_, index) => index).sort((a, b) =>
            this.depth(this.nestedProxyRoots[b]) - this.depth(this.nestedProxyRoots[a]));
        for (const index of indexes) {
            const root = this.nestedProxyRoots[index];
            if (root && root.isValid && index < this.nestedProxyRootActiveBefore.length)
                root.active = this.nestedProxyRootActiveBefore[index];
        }
    }

    private depth(node: Node): number {
        let value = 0; for (let current: Node | null = node; current; current = current.parent) value++; return value;
    }
}
