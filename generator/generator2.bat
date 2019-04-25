:: this script must be executed in this directory
:: all the output goes to generator/output folder
:: .cpp and .h files:
:: cimgui.h and cimgui.cpp with gcc preprocess
:: cimgui_nopreprocess.h and cimgui_nopreprocess.cpp generated without preprocess
:: cimgui_impl.h with implementation function cdefs
:: lua and json files:
:: definitions.lua for function definitions
:: structs_and_enums.lua with struct and enum information-definitions
:: impl_definitions.lua for implementation function definitions

:: set your PATH if necessary for LuaJIT or Lua5.1 or luajit with: (for example)

:: NOT WORKING(compiler cl): set PATH=%PATH%;c:\Users\PO185021\tools\luapower-luajit\bin\mingw64;"c:\Program Files (x86)\Microsoft Visual Studio\2017\BuildTools\VC\Tools\MSVC\14.16.27023\bin\Hostx64\x64\";
set PATH=%PATH%;c:\Users\PO185021\tools\luapower-luajit\bin\mingw64;c:\msys64\mingw64\bin\;

:: set PATH=%PATH%;C:\luaGL;C:\i686-7.2.0-release-posix-dwarf-rt_v5-rev1\mingw32\bin;
:: set PATH=%PATH%;C:\luaGL\sources\luajit-master\luajit-master\bin\mingw32;C:\mingw32\bin;
::process  files
:: arg[1] compiler name gcc, clang, cl or nocompiler
:: arg[2..n] name of implementations to generate
luajit ./generator2.lua gcc glfw opengl3 opengl2 sdl

::leave console open
cmd /k

