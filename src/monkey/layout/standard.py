"""monkey-project/1 fixed locations (docs/PROJECT-SPEC.md). The only module that spells target roots.

Each fixed file is (current, legacy). Candidates whose manifest carries projectLayout=VERSION use the
current path; older frozen candidates resolve the legacy path through their own pathMap.
"""
VERSION='monkey-project/1.0.0'

UNITY_TYPES={'sprite':'Sprites','texture':'Textures','atlas':'Atlases','prefab':'Prefabs','effect':'Effects',
    'animation':'Animations','spine':'Spine','font':'Fonts','music':'Audio/Music','sfx':'Audio/Sfx','voice':'Audio/Voice',
    'material':'Materials','shader':'Shaders','model':'Models','config':'Config','data':'Data','strings':'Strings','video':'Video'}
CREATOR_TYPES={'sprite':'art/sprites','texture':'art/textures','atlas':'art/atlases','prefab':'prefabs','effect':'effects',
    'animation':'animations','spine':'art/spine','font':'fonts','music':'audio/music','sfx':'audio/sfx','voice':'audio/voice',
    'material':'art/materials','shader':'art/shaders','model':'art/models','config':'config','data':'data','strings':'strings','video':'video'}

ROOTS={
    'unity':dict(content='Assets/Game/Content',scenes='Assets/Game/Scenes',game='Assets/Game',conversion='Assets/Game/Editor/Conversion',
        localization='Localization',minigames='MiniGames',unsorted='Unsorted',scripts='Assets/Game/Scripts'),
    'creator':dict(content='assets',scenes='assets/scenes',game='assets',conversion='extensions/monkey-import',
        localization='localization',minigames='mini-games',unsorted='unsorted',scripts='assets/scripts'),
}
SOURCE_RECOVERY='SourceRecovery'
RECOVERY=dict(original='SourceRecovery/Original',unconverted='SourceRecovery/Unconverted',config='SourceRecovery/Config',
    modules='SourceRecovery/Code/Modules',drafts='SourceRecovery/Code/Drafts',source='SourceRecovery/Code/Source',
    thirdParty='SourceRecovery/Code/ThirdParty',excluded='SourceRecovery/Excluded')

_C='Assets/Game/Editor/Conversion/'
UNITY_FILES={
    'importPlan':(_C+'import-plan.json','Assets/Monkey/Editor/import-plan.json'),
    'outputPaths':(_C+'output-paths.json','Analysis/output-paths.json'),
    'importer':(_C+'MonkeyImporter.cs','Assets/Monkey/Editor/MonkeyImporter.cs'),
    'numericCode':(_C+'MonkeyNumericCode.cs','Assets/Monkey/Editor/MonkeyNumericCode.cs'),
    'prefabInstances':(_C+'MonkeyPrefabInstances.cs','Assets/Monkey/Editor/MonkeyPrefabInstances.cs'),
    'dynamicUi':(_C+'MonkeyDynamicUi.cs','Assets/Monkey/Editor/UnityDynamicUi.cs'),
    'previewView':('Assets/Game/Presentation/Preview/ContentPreviewView.cs','Assets/Generated/Views/MonkeyCandidateView.cs'),
    'previewPrefab':('Assets/Game/Scenes/Preview/ContentPreview.prefab','Assets/Generated/Views/Candidate.prefab'),
    'previewScene':('Assets/Game/Scenes/Preview/ContentPreview.unity','Assets/Generated/Scenes/Candidate.unity'),
    'bootScene':('Assets/Game/Scenes/Boot.unity','Assets/Generated/Scenes/ImportBootstrap.unity'),
    'editableProbe':('Assets/Game/Scenes/Preview/EditableProbe.prefab','Assets/Generated/Views/EditableProbe.prefab'),
}
LAYOUT_COMPONENTS=('NativeLinearLayoutGroup.cs','NativeRectConstraints.cs','NativeTextLineBox.cs','IntrinsicGridLayoutGroup.cs')
UNITY_LAYOUT_DIR='Assets/Game/Presentation/Common/Layout'
UNITY_NATIVE_ROOTS=['Assets/Game/Content','Assets/Game/Scenes','Assets/Game/Presentation','Assets/Game/Domain','Assets/TextMesh Pro']
UNITY_META_ROOTS=['Assets/Game/Editor/Conversion']

_E='extensions/monkey-import/'
CREATOR_FILES={
    'importPlan':(_E+'import-plan.json',_E+'import-plan.json'),
    'previewScene':('assets/scenes/preview/ContentPreview.scene','assets/generated/views/Candidate.scene'),
}


def unity(key):return UNITY_FILES[key][0]
def creator(key):return CREATOR_FILES[key][0]


def current(manifest):
    return manifest.get('projectLayout')==VERSION


def locate(manifest,key,engine='unity'):
    """Fixed file path inside a candidate of either layout generation."""
    table=UNITY_FILES if engine=='unity' else CREATOR_FILES
    if current(manifest):return table[key][0]
    from ..targets.layout import lookup
    return lookup(table[key][1],manifest)


def unity_output_paths():
    """Typed Editor host locations (UnityImporter.OutputPaths)."""
    return dict(plan=unity('importPlan'),prefab=unity('previewPrefab'),scene=unity('previewScene'),bootstrap=unity('bootScene'),
        artRoot=ROOTS['unity']['content'],controllersRoot=ROOTS['unity']['content']+'/Animations',materialsRoot=ROOTS['unity']['content']+'/Materials',
        animationsRoot=ROOTS['unity']['content']+'/Animations',sourcePrefabsRoot=ROOTS['unity']['content'],editableProbe=unity('editableProbe'),
        nativeRoots=UNITY_NATIVE_ROOTS,metaRoots=UNITY_META_ROOTS)


def creator_output_paths():
    return dict(scene=creator('previewScene'),prefabs='assets',animations='assets',nativeRoots=['assets'])
