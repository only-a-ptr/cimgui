# Generate C++ sources to bind DearIMGUI to AngelScript
# Use JSON output from CIMGUI project

import json
import sys
import os.path

# Reference: https://github.com/cimgui/cimgui#definitions-description
DEFINITIONS_PATH = 'definitions.json'

def process_global_fn(meta):
    decl = meta['ret'] + " " + meta['funcname'] + "("
    args_str = []
    for arg_meta in meta['argsT']:
        args_str.append(arg_meta['type'] + ' ' + arg_meta['name'])
    decl += ', '.join(args_str) + ')'
                 
    print(decl.ljust(50, ' ') + ' //' + meta['cimguiname'])


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