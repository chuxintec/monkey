import unittest
from monkey.layout import casing
from monkey.layout.allocate import LayoutPlanner
from monkey.layout.overrides import validate
from monkey.layout.verify import scan
from monkey.sources.compiled import ParseError

FOODSTREET={
    'remoteAsset:fish':dict(bundle='remoteAsset',logicalPath='Texture/Element/Fish_3/1005302'),
    'gameAsset:bgm':dict(bundle='gameAsset',logicalPath='Audio/BGM/bgm_Intro'),
    'gameAsset:sfx':dict(bundle='gameAsset',logicalPath='Audio/Merge/sfx_ItemAddpropUse'),
    'zh-tw:label':dict(bundle='zh-tw',logicalPath='Config/label'),
    'zh:label':dict(bundle='zh',logicalPath='Config/label'),
    'remoteAsset:adorn':dict(bundle='remoteAsset',logicalPath='Prefab/House/Adorns/Room7/10070600'),
    'miniGameRes:level':dict(bundle='miniGameRes',logicalPath='Texture/rope3d/resources/levels/level_2'),
    'gameAsset:clip':dict(bundle='gameAsset',logicalPath='Anim/BigDay/PlayerGroup/appear4'),
    'main:scene':dict(bundle='main',logicalPath='main'),
    'main:test':dict(bundle='main',logicalPath='room16_test'),
    'resources:cocos3':dict(bundle='resources',logicalPath='textures/ui/btn_ok/spriteFrame'),
    'resources:music':dict(bundle='resources',logicalPath='music/UI/109'),
    'gameAsset:cfg':dict(bundle='gameAsset',logicalPath='Config/AudioCfg'),
}


class CasingTests(unittest.TestCase):
    def test_words_keep_letter_digit_runs_and_split_case_changes(self):
        self.assertEqual(casing.words('SpArea01'),['Sp','Area01'])
        self.assertEqual(casing.words('UIPanel'),['UI','Panel'])
        self.assertEqual(casing.words('Room7Door'),['Room7','Door'])
        self.assertEqual(casing.words('鹅图标'),['鹅图标'])

    def test_three_casings(self):
        self.assertEqual((casing.pascal('Fish_3'),casing.kebab('Fish_3'),casing.snake('Fish_3')),('Fish3','fish3','fish_3'))
        self.assertEqual(casing.snake('CookGo'),'cook_go')
        self.assertEqual(casing.pascal('ui_main'),'UIMain')
        self.assertEqual(casing.kebab('img_box_23_1'),'img-box23-1')
        self.assertEqual(casing.pascal('10070600'),'10070600')

    def test_unsafe_device_and_long_names(self):
        self.assertEqual(casing.pascal('CON'),'CON_')
        self.assertNotIn('/',casing.snake('a/b'))
        long=casing.snake('x'*200)
        self.assertLessEqual(len(long.encode()),casing.SEGMENT_BYTES)
        self.assertNotEqual(long,casing.snake('x'*199))


class PlannerTests(unittest.TestCase):
    def test_packaging_type_words_and_variants_leave_production_paths(self):
        p=LayoutPlanner('unity',FOODSTREET)
        self.assertEqual(p.path('remoteAsset:fish','sprite','.png'),'Assets/Game/Content/Sprites/Element/Fish3/1005302.png')
        self.assertEqual(p.path('remoteAsset:fish@original','sprite','.png'),'Assets/Game/Content/Sprites/Element/Fish3/1005302_untrimmed.png')
        self.assertEqual(p.path('remoteAsset:adorn','prefab','.prefab'),'Assets/Game/Content/Prefabs/House/Adorns/Room7/10070600.prefab')
        self.assertEqual(p.path('gameAsset:clip','animation','.anim'),'Assets/Game/Content/Animations/BigDay/PlayerGroup/appear4.anim')
        self.assertEqual(p.path('resources:cocos3','sprite','.png'),'Assets/Game/Content/Sprites/UI/btn_ok.png')

    def test_audio_is_never_an_image_and_is_split_by_category(self):
        p=LayoutPlanner('unity',FOODSTREET)
        self.assertEqual(p.path('gameAsset:bgm','native','.mp3'),'Assets/Game/Content/Audio/Music/Common/bgm_intro.mp3')
        self.assertEqual(p.path('gameAsset:sfx','cc.AudioClip','.mp3'),'Assets/Game/Content/Audio/Sfx/Merge/sfx_item_addprop_use.mp3')
        self.assertEqual(p.path('resources:music','native','.mp3'),'Assets/Game/Content/Audio/Sfx/UI/109.mp3')

    def test_locale_bundles_become_localization_and_configs_become_tables(self):
        p=LayoutPlanner('unity',FOODSTREET)
        self.assertEqual(p.path('zh-tw:label','cc.JsonAsset','.json'),'Assets/Game/Content/Localization/zh-Hant/Strings/Label.json')
        self.assertEqual(p.path('zh:label','cc.JsonAsset','.json'),'Assets/Game/Content/Localization/zh-Hans/Strings/Label.json')
        self.assertEqual(p.path('gameAsset:cfg','cc.JsonAsset','.json'),'Assets/Game/Content/Config/Common/AudioTable.json')
        self.assertEqual(p.path('miniGameRes:level','cc.JsonAsset','.json'),'Assets/Game/Content/MiniGames/Rope3d/Config/Levels/Level2.json')

    def test_scenes_and_unknown_sources(self):
        p=LayoutPlanner('unity',FOODSTREET)
        self.assertEqual(p.path('main:scene','scene',''),'Assets/Game/Scenes/Main.unity')
        self.assertEqual(p.path('main:test','scene',''),'Assets/Game/Scenes/Tests/Room16Test.unity')
        hashed=p.path('x:1','native','.png',metadata=dict(bundle='x',logicalPath='native/ab/abcd.png',nameProvenance='input-relative-path'))
        self.assertTrue(hashed.startswith('Assets/Game/Content/Textures/Unsorted/texture_'))
        unsafe=p.path('x:2','native','.png',metadata=dict(bundle='x',logicalPath='../escape'))
        self.assertIn('/Unsorted/',unsafe);self.assertNotIn('..',unsafe)

    def test_creator_uses_lowercase_folders_and_same_modules(self):
        p=LayoutPlanner('creator',FOODSTREET)
        self.assertEqual(p.path('remoteAsset:fish','sprite','.png'),'assets/art/sprites/element/fish3/1005302.png')
        self.assertEqual(p.path('gameAsset:clip','animation','.anim'),'assets/animations/big-day/player-group/appear4.anim')
        self.assertEqual(p.path('zh-tw:label','cc.JsonAsset','.json'),'assets/localization/zh-hant/strings/Label.json')
        self.assertEqual(p.folder('spine:x',metadata=dict(bundle='spineAsset',logicalPath='SpineCook/House/Room9/r9_dianshi1')),'assets/art/spine/house/room9/r9-dianshi1')

    def test_collision_winner_is_independent_of_request_order(self):
        meta={'b:2':dict(bundle='b',logicalPath='UI/Icon'),'a:1':dict(bundle='a',logicalPath='ui/icon'),'c:3':dict(bundle='c',logicalPath='Ui/ICON')}
        requests=[(sid,'sprite','.png','',None,None) for sid in meta]
        first=LayoutPlanner('unity',meta);first.reserve(requests)
        second=LayoutPlanner('unity',meta);second.reserve(list(reversed(requests)))
        mapping=lambda p:{sid:p.path(sid,'sprite','.png') for sid in meta}
        self.assertEqual(mapping(first),mapping(second))
        self.assertEqual(mapping(first)['a:1'],'Assets/Game/Content/Sprites/UI/icon.png')
        self.assertEqual(len({v.casefold() for v in mapping(first).values()}),3)
        self.assertEqual(first.report()['collisionPaths'],2)

    def test_case_variant_folders_merge_into_one_spelling(self):
        p=LayoutPlanner('unity',{'a:1':dict(bundle='a',logicalPath='floorAndWall/x'),'a:2':dict(bundle='a',logicalPath='FloorAndWall/y')})
        one,two=p.path('a:1','sprite','.png'),p.path('a:2','sprite','.png')
        self.assertEqual(one.rsplit('/',1)[0],two.rsplit('/',1)[0])

    def test_existing_claims_from_another_stage_are_not_reused(self):
        p=LayoutPlanner('unity',FOODSTREET);p.claim('Assets/Game/Content/Audio/Music/Common/bgm_intro.mp3')
        self.assertNotEqual(p.path('gameAsset:bgm','native','.mp3'),'Assets/Game/Content/Audio/Music/Common/bgm_intro.mp3')

    def test_layout_overrides_change_paths_only(self):
        overrides=validate(dict(schemaVersion=1,modules=[dict(match='uiraw/icon_*',module='Icons/{1}')],renames={'u:1':'street_sweeper'},
                               bundles={'events':dict(role='minigame')}))
        p=LayoutPlanner('unity',{'u:1':dict(bundle='game',logicalPath='uiraw/icon_item/a2_saodiji3'),
                                 'u:2':dict(bundle='events',logicalPath='Texture/Disco/bg')},overrides)
        self.assertEqual(p.path('u:1','sprite','.png'),'Assets/Game/Content/Sprites/Icons/Item/street_sweeper.png')
        self.assertEqual(p.path('u:2','sprite','.png'),'Assets/Game/Content/MiniGames/Disco/Sprites/Common/bg.png')

    def test_invalid_overrides_are_rejected(self):
        for bad in [dict(schemaVersion=2),dict(schemaVersion=1,extra=1),dict(schemaVersion=1,modules=[dict(match='../x',module='Y')]),
                    dict(schemaVersion=1,modules=[dict(match='a/*',module='{2}')]),dict(schemaVersion=1,renames={'a':'x/y'}),
                    dict(schemaVersion=1,rootNamespace='lower.case'),dict(schemaVersion=1,code={'A':dict(layer='Runtime')})]:
            with self.assertRaises(ParseError):validate(bad)


class ForbiddenNameTests(unittest.TestCase):
    def test_legacy_layout_is_caught_and_canonical_layout_passes(self):
        legacy=['Assets/Game/Content/Images/Sprites/remoteAsset/Texture/Element/Fish_3/1005302.original.png',
                'Assets/Game/Content/Materials/002aba30c8bc53ce83ca705ea6b1b7fb.mat',
                'Assets/Game/Content/Config/Recovered/zh-tw/Config/label.json',
                'Assets/Generated/Views/Candidate.prefab','Assets/Texture2D/6.png','Assets/Resources/config/AudioCfg.bytes',
                'assets/art/images/Original/main/a.png']
        self.assertEqual(len({d['location'] for d in scan(legacy)}),len(legacy))
        p=LayoutPlanner('unity',FOODSTREET)
        clean=[p.path(sid,kind,suffix) for sid,kind,suffix in [('remoteAsset:fish','sprite','.png'),('zh-tw:label','cc.JsonAsset','.json'),
               ('gameAsset:bgm','native','.mp3'),('main:scene','scene',''),('remoteAsset:adorn','prefab','.prefab')]]
        clean+=['Assets/Game/Editor/Conversion/MonkeyImporter.cs','Assets/TextMesh Pro/Shaders/TMP_SDF.shader']
        self.assertEqual(scan(clean),[])

    def test_class_prefix_check_reads_code(self):
        path='Assets/Game/Presentation/Shop/ShopView.cs'
        self.assertTrue(scan([path],{path:'namespace Recovered.Gameplay { public class ShopView {} }'}))
        self.assertFalse(scan([path],{path:'namespace FoodStreet.Presentation.Shop { public class ShopView {} }'}))


if __name__=='__main__':
    unittest.main()
