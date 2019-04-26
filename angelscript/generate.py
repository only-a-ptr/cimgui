# Generate C++ sources to bind DearIMGUI to AngelScript
# Use JSON output from CIMGUI project

import json
import sys
import os.path

# ---------- Config ----------

# Reference: https://github.com/cimgui/cimgui#definitions-description
DEFINITIONS_PATH = 'definitions.json'
OUT_CPP_PATH = 'as-imgui-gen.cpp'
VERBOSE = True # Print debug comments to the output C++ code

# ---------- END Config ----------

f = open(OUT_CPP_PATH, mode='w')
print("""
#include <string>
#include <exception>

// ================================================================================================
//     TODO: move to header
// ================================================================================================

namespace imgui_angelscript 
{

class SetupError: public std::runtime_error  
{
public:
    SetupError(const char* msg): runtime_error(msg) {}
    //const char* what() { return std::runtime_error::what(); }
};

} // namespace imgui_angelscript


// ================================================================================================
//     Registration helper class
// ================================================================================================

using namespace AngelScript;

class Helper
{
public:
    Helper(asIScriptEngine* e): m_engine(e), m_obj_name(nullptr) {}

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
private:
    asIScriptEngine* m_engine;
    const char*      m_obj_name;
};

// ================================================================================================
//     Functions (generated)
// ================================================================================================
""", file=f)

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
        if out_type == '...': # C vararg
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
