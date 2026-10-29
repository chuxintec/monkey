'use strict';
// Editor-side binder for generated disabled static-field carriers.
// NativeCreate has no callbacks; business behavior remains disabled.
const cc = require('cc');

function nativeType(spec) {
    if (!spec || typeof spec.typeName !== 'string' || !spec.typeName)
        throw new Error('STATIC_CARRIER_SPEC_INVALID');
    const ctor = cc.js.getClassByName(spec.typeName);
    if (typeof ctor !== 'function' || !(ctor.prototype instanceof cc.Component))
        throw new Error('STATIC_CARRIER_TYPE_MISSING: ' + spec.typeName);
    if (!guidMatches(spec.scriptGuid, ctor)) throw new Error('STATIC_CARRIER_GUID_MISMATCH: ' + spec.typeName);
    return ctor;
}
function guidMatches(guid, ctor) {
    if (typeof guid !== 'string' || !/^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(guid)) return false;
    try {
        const raw = guid.replace(/-/g, '').toLowerCase();
        const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        let expected = raw.slice(0, 5);
        for (let i = 5; i < 32; i += 3) {
            const value = parseInt(raw.slice(i, i + 3), 16);
            expected += alphabet[value >> 6] + alphabet[value & 63];
        }
        return cc.js.getClassId(ctor, false) === expected;
    } catch (_) { return false; }
}
function gap(gaps, value) { if (!gaps.includes(value)) gaps.push(value); }
function mergeGaps(spec, operational) {
    const all = [];
    for (const value of (spec && spec.gaps) || []) gap(all, value);
    for (const value of operational) gap(all, value);
    return all;
}
function equalArray(left, right) {
    return Array.isArray(left) && Array.isArray(right) && left.length === right.length &&
        left.every((value, index) => value === right[index]);
}
function colorChannels(field) {
    const values = [field.colorR, field.colorG, field.colorB, field.colorA];
    return values.every(value => Number.isInteger(value) && value >= 0 && value <= 255) ? values : null;
}
function refValue(sourceId, resolveRef, gaps, field) {
    if (typeof sourceId !== 'string' || !sourceId || typeof resolveRef !== 'function') {
        gap(gaps, 'reference_resolver_missing:' + field); return null;
    }
    try {
        const value = resolveRef(sourceId);
        if (!value) gap(gaps, 'reference_unresolved:' + field + ':' + sourceId);
        return value || null;
    } catch (error) {
        gap(gaps, 'reference_resolver_failed:' + field + ':' + (error && error.name || 'Error'));
        return null;
    }
}
function expectedValue(field, resolveRef, gaps) {
    if (field.storageType === 'bool') return field.boolValue;
    if (field.storageType === 'double') return field.numberValue;
    if (field.storageType === 'string') return field.mode === 'snapshot-json' ? field.snapshotJson : field.stringValue;
    if (field.storageType === 'Color') {
        const channels = colorChannels(field);
        if (!channels) { gap(gaps, 'color_channels_invalid:' + field.sourceFieldName); return undefined; }
        return new cc.Color(channels[0], channels[1], channels[2], channels[3]);
    }
    if (field.storageType === 'UnityEngine.Object') {
        if (field.nullExpected) return null;
        const value = refValue(field.refValue, resolveRef, gaps, field.sourceFieldName);
        if (value && !validReference(field.kind, value)) {
            gap(gaps, 'reference_type_mismatch:' + field.sourceFieldName);
            return null;
        }
        return value;
    }
    if (field.storageType === 'bool[]') return field.boolValues || [];
    if (field.storageType === 'double[]') return field.numberValues || [];
    if (field.storageType === 'string[]') return field.stringValues || [];
    if (field.storageType === 'UnityEngine.Object[]') {
        const values = (field.refValues || []).map((id, index) => refValue(id, resolveRef, gaps,
            field.sourceFieldName + '[' + index + ']'));
        const kind = field.elementKind;
        if (values.some(value => !value) || values.some(value => !validReference(kind, value))) {
            if (values.some(value => value && !validReference(kind, value))) gap(gaps, 'reference_array_type_mismatch:' + field.sourceFieldName);
            return null;
        }
        return values;
    }
    gap(gaps, 'unsupported_storage:' + field.sourceFieldName);
    return undefined;
}
function recordConstructor(spec, field) {
    const prefix = spec.typeName.slice(0, spec.typeName.lastIndexOf('.'));
    const ctor = cc.js.getClassByName(prefix + '.' + field.recordTypeName);
    if (typeof ctor !== 'function') throw new Error('STATIC_RECORD_TYPE_MISSING: ' + field.recordTypeName);
    return ctor;
}
function assignRecordField(expected, instance, resolveRef, gaps, path) {
    if (!(expected.fieldName in instance)) { gap(gaps, 'record_field_missing:' + path); return false; }
    if (expected.storageType === 'UnityEngine.Object') {
        let value = null;
        if (!expected.nullExpected) {
            value = refValue(expected.refValue, resolveRef, gaps, path);
            if (value && !validReference(expected.referenceKind || expected.kind, value)) {
                gap(gaps, 'reference_type_mismatch:' + path); return false;
            }
            if (!value) return false;
        }
        instance[expected.fieldName] = value;
        return true;
    }
    let value;
    if (expected.storageType === 'bool') value = expected.boolValue;
    else if (expected.storageType === 'double') value = expected.numberValue;
    else if (expected.storageType === 'string') value = expected.stringValue;
    else if (expected.storageType === 'Color') {
        const channels = colorChannels(expected);
        if (!channels) { gap(gaps, 'color_channels_invalid:' + path); return false; }
        value = new cc.Color(channels[0], channels[1], channels[2], channels[3]);
    }
    else { gap(gaps, 'unsupported_record_storage:' + path); return false; }
    instance[expected.fieldName] = value;
    return true;
}
function assignRecords(spec, field, resolveRef, gaps) {
    let ctor;
    try { ctor = recordConstructor(spec, field); }
    catch (_) { gap(gaps, 'record_type_unresolved:' + field.sourceFieldName); return null; }
    const rows = [];
    for (let i = 0; i < (field.recordValues || []).length; i++) {
        const expectedRow = field.recordValues[i];
        const instance = new ctor();
        for (const nested of expectedRow.fields || [])
            assignRecordField(nested, instance, resolveRef, gaps,
                field.sourceFieldName + '[' + i + '].' + nested.sourceFieldName);
        rows.push(instance);
    }
    return rows;
}
function readRecords(field, actual, resolveRef, gaps) {
    const expectedRows = field.recordValues || [];
    if (!Array.isArray(actual) || actual.length !== expectedRows.length) {
        gap(gaps, 'record_array_readback_mismatch:' + field.sourceFieldName); return { verified: false, rows: [] };
    }
    let verified = true;
    const rows = [];
    for (let i = 0; i < expectedRows.length; i++) {
        const instance = actual[i];
        if (!instance || typeof instance !== 'object') {
            gap(gaps, 'record_instance_missing:' + field.sourceFieldName + '[' + i + ']'); verified = false; rows.push({index: i, fields: []}); continue;
        }
        const fields = [];
        for (const expected of expectedRows[i].fields || []) {
            const row = { ...expected };
            if (!(expected.fieldName in instance)) {
                gap(gaps, 'record_field_missing:' + expected.sourceFieldName); verified = false; fields.push(row); continue;
            }
            const value = instance[expected.fieldName];
            if (expected.storageType === 'UnityEngine.Object') {
                if (expected.nullExpected) row.referenceVerified = value === null;
                else {
                    const resolved = refValue(expected.refValue, resolveRef, gaps,
                        field.sourceFieldName + '[' + i + '].' + expected.sourceFieldName);
                    row.referenceVerified = !!resolved && value === resolved &&
                        validReference(expected.referenceKind || expected.kind, value);
                }
                if (!row.referenceVerified) { gap(gaps, 'record_reference_readback_mismatch:' + expected.sourceFieldName); verified = false; }
            } else if (expected.storageType === 'bool') {
                row.boolValue = value;
                if (typeof value !== 'boolean' || value !== expected.boolValue) { gap(gaps, 'record_field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
            } else if (expected.storageType === 'double') {
                row.numberValue = value;
                if (typeof value !== 'number' || !Object.is(value, expected.numberValue)) { gap(gaps, 'record_field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
            } else if (expected.storageType === 'string') {
                row.stringValue = value;
                if (typeof value !== 'string' || value !== expected.stringValue) { gap(gaps, 'record_field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
            } else if (expected.storageType === 'Color') {
                const channels = colorChannels(expected);
                row.colorR = value && value.r; row.colorG = value && value.g;
                row.colorB = value && value.b; row.colorA = value && value.a;
                if (!channels || !(value instanceof cc.Color) || !channels.every((channel, index) =>
                    [value.r, value.g, value.b, value.a][index] === channel)) {
                    gap(gaps, 'record_color_readback_mismatch:' + expected.sourceFieldName); verified = false;
                }
            } else { gap(gaps, 'unsupported_record_storage:' + expected.sourceFieldName); verified = false; }
            fields.push(row);
        }
        rows.push({ index: i, fields });
    }
    return { verified, rows };
}
function validReference(kind, value) {
    if (kind === 'node_ref') return value instanceof cc.Node;
    if (kind === 'component_ref') return value instanceof cc.Component;
    if (kind === 'asset_ref') return value instanceof cc.Asset;
    return false;
}
function sameReference(actual, expected) { return actual === expected; }

function Create(spec, node) {
    if (!node || typeof node.addComponent !== 'function') throw new Error('STATIC_CARRIER_NODE_MISSING: ' + spec.sourceId);
    const component = node.addComponent(nativeType(spec));
    if (!('__monkeySourceId' in component)) throw new Error('STATIC_CARRIER_SOURCE_ID_FIELD_MISSING');
    component.__monkeySourceId = spec.sourceId;
    component.enabled = false;
    return component;
}

function Assign(spec, component, resolveRef) {
    const gaps = [];
    const nativeGaps = [];
    let typeMatches = false;
    if (!spec || !component) return { sourceId: spec && spec.sourceId, fieldsVerified: false, enabled: false, fields: [], gaps: ['carrier_missing'] };
    try {
        typeMatches = component.constructor === nativeType(spec);
        if (!typeMatches) gap(gaps, 'carrier_type_mismatch');
        if (typeMatches && ('__monkeySourceId' in component)) component.__monkeySourceId = spec.sourceId;
        else gap(nativeGaps, 'native_source_id_field_missing');
        for (const field of spec.fields || []) {
            try {
                if (!(field.fieldName in component)) { gap(gaps, 'carrier_field_missing:' + field.sourceFieldName); continue; }
                const value = field.elementKind === 'record' && field.recordTypeName
                    ? assignRecords(spec, field, resolveRef, gaps) : expectedValue(field, resolveRef, gaps);
                if (value === undefined || (field.elementKind === 'record' && value === null) ||
                    (field.storageType.includes('Object') && value === null && !field.nullExpected)) continue;
                component[field.fieldName] = Array.isArray(value) ? value.slice() : value;
            } catch (error) {
                gap(gaps, 'assign_failed:' + field.sourceFieldName + ':' + (error && error.name || 'Error'));
            }
        }
    } catch (error) { gap(gaps, 'carrier_contract_failed:' + (error && error.name || 'Error')); }
    component.enabled = false;
    const fieldsAssigned = gaps.length === 0;
    const nativeScriptGuid = component && guidMatches(spec.scriptGuid, component.constructor) ? spec.scriptGuid : null;
    if (!nativeScriptGuid) gap(nativeGaps, 'native_script_guid_mismatch');
    if (component.__monkeySourceId !== spec.sourceId) gap(nativeGaps, 'native_source_id_mismatch');
    const nativeIdentityVerified = typeMatches && nativeGaps.length === 0;
    for (const value of nativeGaps) gap(gaps, value);
    return { sourceId: spec.sourceId, typeName: spec.typeName, scriptGuid: spec.scriptGuid,
        nativeSourceId: component.__monkeySourceId, nativeScriptGuid, nativeIdentityVerified,
        fieldsVerified: false, fieldsAssigned, enabled: false, fields: (spec.fields || []).map(field => ({ ...field })),
        gaps: mergeGaps(spec, gaps), nativeComplete: false };
}

function Read(spec, component, resolveRef) {
    const gaps = [];
    const nativeGaps = [];
    const fields = [];
    let verified = !!spec && !!component;
    let typeMatches = false;
    try {
        typeMatches = !!spec && !!component && component.constructor === nativeType(spec);
        if (!typeMatches) {
            gap(gaps, 'carrier_type_mismatch'); verified = false;
        } else {
            for (const expected of spec.fields || []) {
                const row = { ...expected };
                if (!(expected.fieldName in component)) {
                    gap(gaps, 'carrier_field_missing:' + expected.sourceFieldName); verified = false; fields.push(row); continue;
                }
                const actual = component[expected.fieldName];
                if (expected.elementKind === 'record' && expected.recordTypeName) {
                    const read = readRecords(expected, actual, resolveRef, gaps);
                    row.recordValues = read.rows;
                    if (!read.verified) verified = false;
                } else if (expected.storageType === 'UnityEngine.Object') {
                    if (expected.nullExpected) {
                        row.referenceVerified = actual === null;
                    } else {
                        const resolved = refValue(expected.refValue, resolveRef, gaps, expected.sourceFieldName);
                        row.referenceVerified = !!resolved && sameReference(actual, resolved);
                    }
                    if (!row.referenceVerified) { gap(gaps, 'reference_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'UnityEngine.Object[]') {
                    const resolved = expectedValue(expected, resolveRef, gaps);
                    row.referencesVerified = Array.isArray(resolved) && equalArray(actual, resolved);
                    if (!row.referencesVerified) { gap(gaps, 'reference_array_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'bool') {
                    row.boolValue = actual;
                    if (typeof actual !== 'boolean' || actual !== expected.boolValue) { gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'double') {
                    row.numberValue = actual;
                    if (typeof actual !== 'number' || !Object.is(actual, expected.numberValue)) { gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'string') {
                    row.stringValue = actual;
                    if (typeof actual !== 'string' || actual !== (expected.mode === 'snapshot-json' ? expected.snapshotJson : expected.stringValue)) {
                        gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false;
                    }
                } else if (expected.storageType === 'Color') {
                    const channels = colorChannels(expected);
                    row.colorR = actual && actual.r; row.colorG = actual && actual.g;
                    row.colorB = actual && actual.b; row.colorA = actual && actual.a;
                    if (!channels || !(actual instanceof cc.Color) || !channels.every((channel, index) =>
                        [actual.r, actual.g, actual.b, actual.a][index] === channel)) {
                        gap(gaps, 'color_readback_mismatch:' + expected.sourceFieldName); verified = false;
                    }
                } else if (expected.storageType === 'bool[]') {
                    row.boolValues = Array.isArray(actual) ? actual.slice() : [];
                    if (!equalArray(actual, expected.boolValues || [])) { gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'double[]') {
                    row.numberValues = Array.isArray(actual) ? actual.slice() : [];
                    if (!equalArray(actual, expected.numberValues || [])) { gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else if (expected.storageType === 'string[]') {
                    row.stringValues = Array.isArray(actual) ? actual.slice() : [];
                    if (!equalArray(actual, expected.stringValues || [])) { gap(gaps, 'field_readback_mismatch:' + expected.sourceFieldName); verified = false; }
                } else { gap(gaps, 'unsupported_storage:' + expected.sourceFieldName); verified = false; }
                fields.push(row);
            }
        }
    } catch (error) { gap(gaps, 'read_failed:' + (error && error.name || 'Error')); verified = false; }
    const wasEnabled = !!(component && component.enabled);
    if (wasEnabled) { component.enabled = false; gap(nativeGaps, 'behavior_enabled'); }
    const nativeSourceId = component && component.__monkeySourceId;
    if (nativeSourceId !== (spec && spec.sourceId)) gap(nativeGaps, 'native_source_id_mismatch');
    const nativeScriptGuid = spec && component && guidMatches(spec.scriptGuid, component.constructor) ? spec.scriptGuid : null;
    if (!nativeScriptGuid) gap(nativeGaps, 'native_script_guid_mismatch');
    const nativeIdentityVerified = typeMatches && nativeGaps.length === 0;
    const fieldsVerified = verified && gaps.length === 0;
    for (const value of nativeGaps) gap(gaps, value);
    return { sourceId: spec && spec.sourceId, nativeSourceId, typeName: spec && spec.typeName,
        scriptGuid: spec && spec.scriptGuid, nativeScriptGuid,
        nativeIdentityVerified, fieldsVerified,
        enabled: false, fields, gaps: mergeGaps(spec, gaps),
        nativeComplete: fieldsVerified && nativeIdentityVerified && !wasEnabled && !!spec.declarationDefaultsVerified &&
            (!Array.isArray(spec.gaps) || spec.gaps.length === 0), dynamicBehaviorComplete: false };
}

module.exports = { Create, Assign, Read };
