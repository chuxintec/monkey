'use strict';
// Editor-only checks for compiler-generated numeric-call subsets. No source methods run.
const cc=require('cc');
function type(spec) {
    if(!/^[A-Za-z_][A-Za-z0-9_]*$/.test(spec.codeClassName||''))throw Error('Invalid generated class name');
    const ctor=cc.js.getClassByName(spec.codeClassName);
    if(typeof ctor!=='function'||!(ctor.prototype instanceof cc.Label))throw Error('Generated Label class not registered: '+spec.codeClassName);
    return ctor;
}
function methods(component,spec) {
    const info=spec.numericMethods;
    if(!info||!['setter','getter'].every(key=>/^[A-Za-z_][A-Za-z0-9_]*$/.test(info[key]||''))||typeof component[info.setter]!=='function'||typeof component[info.getter]!=='function')throw Error('Generated numeric methods missing');
    return {set:value=>component[info.setter](value),get:()=>component[info.getter]()};
}
function exercise(entries) {
    if(!entries.length)return [];
    const ports=entries.map(({component,spec})=>methods(component,spec));
    if(ports.some(p=>p.get()!==undefined))throw Error('Uninitialized generated value changed');
    const report=[];
    entries.forEach(({component,spec},index)=>{
        const text=component.string,font=component.font;
        for(const value of [0,-0,1,Number.MAX_VALUE,NaN,Infinity,-Infinity]) {
            ports[index].set(value);
            if(!Object.is(ports[index].get(),value)||ports.slice(index+1).some(p=>p.get()!==undefined))throw Error('Generated numeric state/instance semantics differ');
            if(component.string!==text||component.font!==font)throw Error('Generated setter changed source presentation');
        }
        report.push({sourceId:spec.sourceId,sourceScriptIdentity:spec.sourceScriptIdentity,className:cc.js.getClassName(component),classId:cc.js.getClassId(component.constructor,false),numberBoundaries:true,instancesIndependent:true,textUnchanged:true});
    });
    return report;
}
function read(component,spec) {
    if(!(component instanceof type(spec))||methods(component,spec).get()!==undefined)throw Error('Reopened generated component/type/state differs');
    const classId=cc.js.getClassId(component.constructor,false);
    if(typeof classId!=='string'||!classId)throw Error('Native script identity missing');
    return {sourceId:spec.sourceId,sourceScriptIdentity:spec.sourceScriptIdentity,className:cc.js.getClassName(component),classId,componentUuid:component.uuid,nodeUuid:component.node.uuid,uninitialized:true};
}
module.exports={type,exercise,read};
