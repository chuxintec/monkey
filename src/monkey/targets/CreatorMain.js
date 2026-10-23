'use strict';
// Creator-only, explicitly invoked. No source scripts are loaded or run.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const execution=require('./execution.js');
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const req = (message, ...args) => Editor.Message.request('asset-db', message, ...args);
function within(root, relative) {
    if (typeof relative !== 'string' || path.isAbsolute(relative) || relative.split(/[\\/]/).includes('..')) throw Error('Unsafe relative path');
    const dest = path.resolve(root, relative);
    let cursor = dest;
    while (cursor !== path.dirname(cursor)) {
        if (fs.existsSync(cursor) && fs.lstatSync(cursor).isSymbolicLink()) throw Error('Symlink path');
        cursor = path.dirname(cursor);
    }
    if (!dest.startsWith(root + path.sep)) throw Error('Path escapes candidate');
    return dest;
}
module.exports = {
    load() {execution.start(()=>module.exports.methods.importCandidate()).catch(error=>console.error('MONKEY_NATIVE_BOOTSTRAP_FAILED: '+String(error.message||error).slice(0,1024)));}, unload() {execution.stop();},
    methods: {
        async importCandidate() {
            const root = path.resolve(Editor.Project.path);
            const manifestRaw = fs.readFileSync(within(root, 'manifest.json'));
            const manifest = JSON.parse(manifestRaw);
            const planRaw = fs.readFileSync(path.join(__dirname, 'import-plan.json'));
            const plan = JSON.parse(planRaw);
            const project = JSON.parse(fs.readFileSync(within(root, 'package.json'), 'utf8'));
            if (manifest.targetProfile !== 'cocos-3.8.8' || project.creator.version !== '3.8.8' || Editor.App.version !== '3.8.8' || project.uuid !== plan.projectUuid || manifest.projectUuid !== project.uuid) throw Error('Wrong Creator/project');
            if (fs.existsSync(within(root, 'assets/generated/views/Candidate.scene')) || fs.existsSync(within(root, 'Analysis/editor-readback.json'))) throw Error('Native output exists; use a fresh candidate');
            // Creator import legitimately edits metas; all original content and glue must still match.
            for (const f of manifest.files) {
                if (f.path.startsWith('assets/') && f.path.endsWith('.meta')) continue;
                if (hash(fs.readFileSync(within(root, f.path))) !== f.sha256) throw Error('Generated content changed: ' + f.path);
            }
            for(const a of plan.animations||[])if(a.convertible&&fs.existsSync(within(root,a.path)))throw Error('Animation output exists; use fresh candidate');
            for(const p of plan.sourcePrefabs||[]) {
                if(!p.path.startsWith('assets/generated/prefabs/')||!p.path.endsWith('.prefab'))throw Error('Unsafe prefab path');
                if(fs.existsSync(within(root,p.path)))throw Error('Prefab output exists; use fresh candidate');
            }
            if (!(await req('query-ready'))) throw Error('Asset database not ready');
            const assets = [];
            for (const a of plan.assets) {
                execution.checkpoint('textures',assets.length,plan.assets.length);
                const url = 'db://' + a.path;
                await req('refresh-asset', url);
                let info = await req('query-asset-info', url);
                if (!info || info.invalid || info.uuid !== a.uuid) throw Error('Native asset import/identity mismatch: ' + a.path);
                if (a.kind === 'sprite') {
                    const m = await req('query-asset-meta', a.uuid);
                    const spriteEntries = Object.values(m.subMetas || {}).filter(s => s.importer === 'sprite-frame');
                    if (spriteEntries.length !== 1) throw Error('Expected exactly one native sprite-frame');
                    const sm = spriteEntries[0]; const u = sm.userData;
                    const [left, top, right, bottom] = a.border;
                    Object.assign(u, {trimType: 'custom', rotated: false, trimX: (a.trimOrigin || [0,0])[0], trimY: (a.trimOrigin || [0,0])[1],
                        width: a.size[0], height: a.size[1], rawWidth: a.originalSize[0], rawHeight: a.originalSize[1],
                        offsetX: a.offset[0], offsetY: a.offset[1], borderLeft: left, borderTop: top, borderRight: right, borderBottom: bottom});
                    // Subresource IDs are assigned by the native importer and retained, never synthesized.
                    await req('save-asset-meta', a.uuid, JSON.stringify(m));
                    await req('refresh-asset', url);
                    info = await req('query-asset-info', url);
                    const sf = await req('query-asset-info', url + '/spriteFrame');
                    const texture = await req('query-asset-info', url + '/texture');
                    if (!sf || !texture || sf.invalid || texture.invalid) throw Error('Native subresource missing: ' + url);
                    assets.push({...a, spriteFrameUuid: sf.uuid, textureUuid: texture.uuid});
                } else assets.push({...a});
            }
            execution.checkpoint('hierarchy',0,plan.nodes.length);
            const nativeDeadlineMs=execution.deadlineMs();
            const options = {name: 'monkey-import', method: 'assemble', args: [{...plan, assets,nativeDeadlineMs}]};
            const result = await Editor.Message.request('scene', 'execute-scene-script', options);
            if (!result || typeof result.serialized !== 'string') throw Error('No native scene serialization');
            const animationAssets=[];
            for(const a of result.animationAssets||[]) {
                if(!a.path.startsWith('assets/generated/animations/')||!a.path.endsWith('.anim'))throw Error('Unsafe animation path');
                within(root,a.path);
                const info=await req('create-asset','db://'+a.path,a.serialized,{overwrite:false,rename:false});
                if(!info||info.invalid)throw Error('Native animation save failed');
                animationAssets.push({id:a.id,uuid:info.uuid,path:a.path});
            }
            const savedPrefabs=[];
            const expectedPrefabs=new Map((plan.sourcePrefabs||[]).map(p=>[p.sourceId,p]));
            if((result.sourcePrefabs||[]).length!==expectedPrefabs.size)throw Error('Prefab serialization count mismatch');
            for(const p of result.sourcePrefabs||[]) {
                execution.checkpoint('source-prefabs',savedPrefabs.length,(plan.sourcePrefabs||[]).length);
                const spec=expectedPrefabs.get(p.sourceId);
                if(!spec||p.path!==spec.path||typeof p.serialized!=='string')throw Error('Unexpected prefab serialization');
                const dest=within(root,p.path);
                fs.mkdirSync(path.dirname(dest),{recursive:true});
                await req('refresh-asset','db://'+path.posix.dirname(p.path));
                const info=await req('create-asset','db://'+p.path,p.serialized,{overwrite:false,rename:false});
                if(!info||info.invalid)throw Error('Native prefab save failed: '+p.sourceId);
                savedPrefabs.push({sourceId:p.sourceId,path:p.path,uuid:info.uuid});expectedPrefabs.delete(p.sourceId);
            }
            execution.checkpoint('candidate-save');
            const scene = await req('create-asset', 'db://assets/generated/views/Candidate.scene', result.serialized, {overwrite: false, rename: false});
            if (!scene || scene.invalid) throw Error('Native scene save failed');
            // Re-load saved/imported scene through the engine asset manager, not the in-memory tree.
            execution.checkpoint('native-readback');
            const saved = await Editor.Message.request('scene', 'execute-scene-script', {name:'monkey-import',method:'readSaved',args:[scene.uuid,{...plan,assets,animationAssets,savedPrefabs,nativeDeadlineMs}]});
            const nativeFiles = [];
            function collect(relative) {
                const folder = within(root, relative);
                for (const name of fs.readdirSync(folder).sort()) {
                    const rel = relative + '/' + name; const full = within(root, rel);
                    if (fs.lstatSync(full).isDirectory()) collect(rel);
                    else nativeFiles.push({path: rel, sha256: hash(fs.readFileSync(full))});
                }
            }
            collect('assets/generated');
            const rb = {...saved, assets, sceneUuid:scene.uuid, creatorVersion:Editor.App.version, projectUuid:project.uuid,
                manifestSha256:hash(manifestRaw), nativeFiles};
            fs.writeFileSync(within(root,'Analysis/editor-readback.json'),JSON.stringify(rb,null,2)+'\n',{flag:'wx'});
            return {sceneUuid:scene.uuid,nodeCount:rb.nodeCount,editorValidation:'readback-recorded'};
        }
    }
};
