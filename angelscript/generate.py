# Generate C++ sources to bind DearIMGUI to AngelScript
# Use JSON output from CIMGUI project

import json
import sys
import os.path

# ---------- Config ----------

# Reference: https://github.com/cimgui/cimgui#definitions-description
DEFINITIONS_PATH = 'definitions.json'
STRUCTS_ENUMS_PATH = 'structs_and_enums.json'
OUT_CPP_PATH = 'as-imgui-gen.cpp'
VERBOSE = True # Print debug comments to the output C++ code

# ---------- END Config ----------

f = open(OUT_CPP_PATH, mode='w')
print("""
#include "as-imgui.hpp"
#include <string>

// ================================================================================================
//     Registration helper class
// ================================================================================================

class Helper
{
public:
    Helper(asIScriptEngine* e): m_engine(e), m_obj_name(nullptr), m_enum_name(nullptr) {}

    void SetActiveObject(const char* name)
    {
        m_obj_name = name;
    }

    void SetNamespace(const char* name)
    {
        int res = m_engine->SetDefaultNamespace(name);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("SetDefaultNamespace() failed"); // TODO: more descriptive!
        }
    }

    void RegObject(const char* name, size_t size, asDWORD flags)
    {
        int res = m_engine->RegisterObjectType(name, size, flags);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterObjectType() failed"); // TODO: more descriptive!
        }
        this->SetActiveObject(name);
    }

    void RegBehaviour(asEBehaviours behav, const char* decl, const asSFuncPtr & ptr, asDWORD flags = asCALL_CDECL_OBJFIRST)
    {
        int res = m_engine->RegisterObjectBehaviour(m_obj_name, behav, decl, ptr, flags);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterObjectBehaviour() failed"); // TODO: more descriptive!
        }
    }
    
    void RegProperty(const char* decl, size_t offset)
    {
        int res = m_engine->RegisterObjectProperty(m_obj_name, decl, offset);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterObjectProperty() failed"); // TODO: more descriptive!
        }
    }    

    void RegConstructor(const char* decl, const asSFuncPtr & ptr)
    {
        this->RegBehaviour(asBEHAVE_CONSTRUCT, decl, ptr);
    }

    void RegDestructor(const char* decl, const asSFuncPtr & ptr)
    {
        this->RegBehaviour(asBEHAVE_DESTRUCT, decl, ptr);
    }

    void RegMethod(const char* decl, const asSFuncPtr & ptr, asDWORD flags = asCALL_CDECL_OBJFIRST)
    {
        int res = m_engine->RegisterObjectMethod(m_obj_name, decl, ptr, flags);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterObjectMethod() failed"); // TODO: more descriptive!
        }
    }

    void RegFunction(const char* name, const asSFuncPtr & ptr, asDWORD flags = asCALL_CDECL)
    {
        int res = m_engine->RegisterGlobalFunction(name, ptr, flags);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterGlobalFunction() failed"); // TODO: more descriptive!
        }
    }
    
    void RegEnum(const char* name)
    {
        int res = m_engine->RegisterEnum(name);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterEnum() failed"); // TODO: more descriptive!
        }
    }
    
    void RegEnumVal(const char* name, int value)
    {
        int res = m_engine->RegisterEnumValue(m_enum_name, name, value);
        if (res < asSUCCESS)
        {
            throw imgui_angelscript::SetupError("RegisterEnumValue() failed"); // TODO: more descriptive!
        }
    }    
private:
    asIScriptEngine* m_engine;
    const char*      m_obj_name;
    const char*      m_enum_name;
};

/// @throws SetupException on error
void imgui_angelscript::RegisterInterface(asIScriptEngine *engine)
{
    Helper h(engine);
""", file=f)

print("""
// ================================================================================================
//     Enums (generated)
// ================================================================================================""", file=f)

structs_and_enums = json.load(open(STRUCTS_ENUMS_PATH))
enums = structs_and_enums['enums']
for enum_name in enums:
    if VERBOSE:
        print('\n//{}'.format(enum_name), file=f)
    print('h.RegEnum({});'.format(enum_name), file=f)
    for meta in enums[enum_name]:
        print('  h.RegEnumValue({}, ({}));'.format(meta['name'], meta['value']), file=f);
        
print("""
// ================================================================================================
//     Structs (generated)
// ================================================================================================""", file=f)

def process_struct(st_name, fields):
    if VERBOSE:
        print('\n//{}'.format(st_name), file=f);
    flags = ['asOBJ_VALUE']
    if st_name in ['ImVec2', 'ImVec4']:
        flags.append('asOBJ_APP_CLASS_ALLFLOATS')
    print('h.RegObject("{}", sizeof({}), {});'.format(st_name, st_name, '|'.join(flags)), file=f);
    for field in fields:
        print('  h.RegProperty("{} {}", offsetof({}, {}));'.format(field['type'], field['name'], st_name, field['name']), file=f)        
    

structs = structs_and_enums['structs']

ST_PRIORITY = [ 'ImVec2', 'ImVec4', 'ImColor' ] # Must be registered first, in this order

for st_name in ST_PRIORITY:
    if st_name in structs:
        process_struct(st_name, structs[st_name])

for st_name in structs:
    if st_name not in ST_PRIORITY:
        process_struct(st_name, structs[st_name])

print("""
// ================================================================================================
//     Functions (generated)
// ================================================================================================""", file=f)

FN_BLACKLIST = [
    # C Vararg helpers
    'igBulletTextV', 'igTextColoredV', 'igTextDisabledV', 'igTextWrappedV', 'igTextV', 'igTreeNodeExV', 'igTreeNodeV', 'igLabelTextV', 'igSetTooltipV',
    # Too low-level for our scripting interface
    'igCaptureKeyboardFromApp', 'igCaptureMouseFromApp', 'igMemAlloc', 'igMemFree', 'igSaveIniSettingsToDisk', 'igSaveIniSettingsToMemory', 'SetAllocatorFunctions',
    # Logging - disabled now for simplicity, to be done
    'LogToTTY', 'LogToFile', 'LogToClipboard', 'LogText', 'LogButtons', 'LogFinish',     
]

def process_global_fn(meta):
    if meta['cimguiname'] in FN_BLACKLIST:
        if VERBOSE:
            print('\n//{}{} -- Blacklisted'.format(meta['cimguiname'], meta['signature']), file=f)
        return
        
    decl = meta['ret'] + " " + meta['funcname'] + "("
    out_args = []
    for arg_meta in meta['argsT']:
        out_type = arg_meta['type']
        out_name = arg_meta['name']
        if out_type == '...': # C vararg arguments
            continue # The associated format string gets replaced by 'string'
        if out_type == 'const char*':
            out_type = 'string' # Just use wrapped std::string or whatever
            if out_name == 'fmt' or out_name == 'format':
                out_name = 'txt'        
        out_args.append(out_type + ' ' + out_name)
    decl += ', '.join(out_args) + ')'
    
    if VERBOSE:
        print('\n//{}{}'.format(meta['cimguiname'], meta['signature']), file=f)             
    print('h.RegFunction("{}", asFUNCTION({}::{}));'.format(decl.ljust(75, ' '), meta['namespace'], meta['funcname']), file=f)


if not os.path.exists(DEFINITIONS_PATH):
    print("defintions JSON not found:", DEFINITIONS_PATH)
    sys.exit()
   
definitions = json.load(open(DEFINITIONS_PATH))


for name in definitions:
    overloads = definitions[name]
    for entry in overloads:
        stname = entry["stname"] 
        if stname == "":
            # global function
            process_global_fn(entry)
        else:
            pass

print("} // void RegisterInterface()", file=f)
f.close()