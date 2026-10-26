import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from monkey.code_configuration import prepare_assets


ROOT = Path(__file__).resolve().parents[1]
UNITY = ROOT / 'outputs/foodstreet-unified-textures/UnityProject'
TABLE = UNITY / 'Assets/Game/Content/Config/Base/ElementMultiOrderPool.json'
SOURCE = UNITY / 'SourceRecovery/Code/Source/snapshot/_subpackages_main_/subpackages/main/game.js'
CANDIDATE = ROOT / '.private/v060-csharp-20261026/foodstreet-code-candidate-03'
EXPECTED = [1010204, 1005303, 1007206, 1002401, 1007204, 1010201,
            1004302, 1005203, 1010303]


class RecipeJsonRuntimeTests(unittest.TestCase):
    def test_offline_csharp_reader_builds_candidate_dish_map_and_flattens_real_json(self):
        if shutil.which('dotnet') is None or not TABLE.is_file() or not SOURCE.is_file():
            self.skipTest('dotnet SDK or pinned private FoodStreet evidence is unavailable')
        candidate_manifest = json.loads((CANDIDATE / 'manifest.json').read_text(encoding='utf-8'))
        file_hashes = {entry['path']: entry['sha256'] for entry in candidate_manifest['files']}
        candidate_sources = {
            'Assets/Game/Domain/Recovered/CodeCollections.cs': CANDIDATE / 'Assets/Game/Domain/Recovered/CodeCollections.cs',
            'Assets/Game/Domain/Recovered/RecoveredRecords.cs': CANDIDATE / 'Assets/Game/Domain/Recovered/RecoveredRecords.cs',
            'Assets/Game/Domain/Recovered/RecipeCatalog.cs': CANDIDATE / 'Assets/Game/Domain/Recovered/RecipeCatalog.cs',
        }
        for relative, path in candidate_sources.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), file_hashes[relative])

        work_parent = ROOT / '.private/v060-csharp-20261026/configuration/runtime-harness'
        work_parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix='runtime-run-', dir=work_parent))
        prepared = work / 'prepared-assets'
        result = prepare_assets(TABLE, SOURCE, prepared)
        prepared_json = prepared / 'Assets/Game/Content/Config/Base/ElementMultiOrderPool.json'
        self.assertEqual(prepared_json.read_bytes(), TABLE.read_bytes())
        self.assertEqual(hashlib.sha256(prepared_json.read_bytes()).hexdigest(),
                         'ac76070e3347e32bb7149c049ab2477b1c46a8bb2768d21195100afd6d85e89d')
        self.assertEqual((prepared_json.parent / (prepared_json.name + '.meta')).read_bytes(),
                         TABLE.with_name(TABLE.name + '.meta').read_bytes())

        project = work / 'project'
        if project.exists():
            shutil.rmtree(project)
        project.mkdir()
        for relative, path in candidate_sources.items():
            destination = project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        reader = prepared / 'Assets/Game/Domain/Recovered/RecipeJsonConfiguration.cs'
        shutil.copyfile(reader, project / 'Assets/Game/Domain/Recovered/RecipeJsonConfiguration.cs')
        (project / 'Program.cs').write_text(
            'using System;\nusing System.IO;\nusing System.Linq;\n'
            'using Game.Domain.Recovered;\n'
            'internal static class Program {\n'
            '  static int Main(string[] args) {\n'
            '    if (args.Length > 1 && args[1] == "reject") {\n'
            '      try { RecipeJsonConfiguration.Load(File.ReadAllText(args[0])); }\n'
            '      catch (InvalidDataException) { Console.WriteLine("rejected"); return 0; }\n'
            '      throw new Exception("unsupported configuration was accepted");\n'
            '    }\n'
            '    RecipeCatalog._dishMap = RecipeJsonConfiguration.Load(File.ReadAllText(args[0]));\n'
            '    if (!RecipeCatalog.IsDish(2015015d)) throw new Exception("dish lookup failed");\n'
            '    int count = 0; RecipeCatalog._dishMap.ForEach((recipe, dish) => count++);\n'
            '    if (count != 732) throw new Exception("unexpected recipe count: " + count);\n'
            '    var leaves = RecipeCatalog.FlattenIngredientsOf(2015015d);\n'
            '    var expected = new double[] {' + ','.join(str(x) + 'd' for x in EXPECTED) + '};\n'
            '    if (!leaves.SequenceEqual(expected)) throw new Exception("flatten mismatch: " + string.Join(",", leaves));\n'
            '    Console.WriteLine("dish=2015015 rows=" + count + " leaves=" + string.Join(",", leaves));\n'
            '    return 0;\n  }\n}\n', encoding='utf-8')
        (project / 'Harness.csproj').write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            ' <PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework>'
            '<ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable></PropertyGroup>\n'
            '</Project>\n', encoding='utf-8')
        offline_sources = work / 'empty-nuget-sources'
        offline_sources.mkdir(exist_ok=True)
        env = dict(__import__('os').environ, DOTNET_CLI_TELEMETRY_OPTOUT='1',
                   DOTNET_SKIP_FIRST_TIME_EXPERIENCE='1', NUGET_PACKAGES=str(work / 'nuget-cache'))
        restore = subprocess.run(['dotnet', 'restore', 'Harness.csproj', '--source', str(offline_sources),
                                  '--ignore-failed-sources', '--nologo'], cwd=project, env=env,
                                 text=True, capture_output=True, timeout=120)
        self.assertEqual(restore.returncode, 0, restore.stdout + restore.stderr)
        build = subprocess.run(['dotnet', 'build', 'Harness.csproj', '--no-restore', '--configuration', 'Release',
                                '--nologo'], cwd=project, env=env,
                               text=True, capture_output=True, timeout=120)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        run = subprocess.run(['dotnet', 'run', '--no-build', '--configuration', 'Release', '--', str(prepared_json)],
                             cwd=project, env=env, text=True, capture_output=True, timeout=60)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn('dish=2015015 rows=732 leaves=' + ','.join(map(str, EXPECTED)), run.stdout)
        invalid_tables = [
            {'1': {'id': 1, 'elementOrderId': -1, 'needElements': {'4': 1},
                   'elementIdWeight': {'900': 0}, 'duration': 1, 'cookType': 1},
             '2': {'id': 2, 'elementOrderId': -1, 'needElements': {'5': 1},
                   'elementIdWeight': {'900': 0}, 'duration': 1, 'cookType': 1}},
            {'1': {'id': 1, 'elementOrderId': -1, 'needElements': {'4': 1, '04': 2},
                   'elementIdWeight': {'900': 0}, 'duration': 1, 'cookType': 1}},
            {'1': {'id': 1, 'elementOrderId': -1, 'needElements': {'901': 1},
                   'elementIdWeight': {'900': 0}, 'duration': 1, 'cookType': 1},
             '2': {'id': 2, 'elementOrderId': -1, 'needElements': {'900': 1},
                   'elementIdWeight': {'901': 0}, 'duration': 1, 'cookType': 1}},
            {'1': {'id': 1, 'elementOrderId': -1, 'needElements': {'9007199254740992': 1},
                   'elementIdWeight': {'900': 0}, 'duration': 1, 'cookType': 1}},
        ]
        exe = project / 'bin/Release/net8.0/Harness.dll'
        for index, invalid in enumerate(invalid_tables):
            invalid_path = work / ('invalid-' + str(index) + '.json')
            invalid_path.write_text(json.dumps(invalid, separators=(',', ':')), encoding='utf-8')
            rejected = subprocess.run(['dotnet', str(exe), str(invalid_path), 'reject'], cwd=project,
                                      env=env, text=True, capture_output=True, timeout=60)
            self.assertEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
            self.assertIn('rejected', rejected.stdout)
        receipt = dict(status='offline-target-reader-behavior-pass', prepareResult=result,
                       restore=restore.stdout, build=build.stdout, run=run.stdout,
                       targetRejectedCases=len(invalid_tables),
                       unityTextAssetOverload='not_compiled_outside_Unity', unityEditor='not_run')
        (work / 'runtime-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False,
            sort_keys=True, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    unittest.main()
