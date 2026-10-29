import subprocess,shutil,unittest
from pathlib import Path
class CreatorTogglePersistenceTests(unittest.TestCase):
 def test_false_checked_state_survives_native_backing_field_roundtrip(self):
  node=shutil.which('node')
  if not node:self.skipTest('Node unavailable')
  js=r'''
const Module=require('module'),original=Module._load;
class Color{constructor(r,g,b,a){Object.assign(this,{r,g,b,a})}}
class Node{constructor(){this.components=[]}getComponent(T){return this.components.find(c=>c instanceof T)||null}addComponent(T){const c=new T();c.node=this;this.components.push(c);return c}}
class Toggle{constructor(){this.enabled=true;this._isChecked=true;this.interactable=true;this.normalColor=new Color(255,255,255,255);this.checkMark=null;this.target=null;this.transition=0}get isChecked(){return this._isChecked}setIsCheckedWithoutNotify(v){this._isChecked=v}}
class ToggleContainer{} class Sprite{}
Module._load=function(r){if(r==='cc')return {Node,Toggle,ToggleContainer,Sprite,Color};return original.apply(this,arguments)};
const api=require(process.argv[1]),n=new Node(),spec={bindings:[{sourceId:'toggle',kind:'cc.Toggle',nodeSourceId:'node',checkedPresent:true,checkedValue:false,interactablePresent:true,interactableValue:true,targetPresent:true,targetSourceId:'node',checkMarkPresent:true,checkMarkSourceId:null,gaps:[]}]};
const gaps=api.Create(spec,id=>id==='node'?n:null,()=>null);if(gaps.length)throw Error(gaps.join(','));
const t=n.getComponent(Toggle),saved=JSON.parse(JSON.stringify({_isChecked:t._isChecked,enabled:t.enabled,interactable:t.interactable}));
const reloaded=new Toggle();Object.assign(reloaded,saved);reloaded.node=n;reloaded.target=n;n.components=[reloaded];
const result=api.Read(spec,id=>id==='node'?n:null,()=>null);if(!result.fields[0].verified||reloaded.isChecked!==false)throw Error('false state not persisted');
'''
  r=subprocess.run([node,'-e',js,str(Path('src/monkey/targets/CreatorStaticToggle.js').resolve())],capture_output=True,text=True)
  self.assertEqual(r.returncode,0,r.stderr)
