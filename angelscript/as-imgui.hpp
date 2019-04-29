#pragma once

#include <angelscript.h>
#include <exception>

namespace imgui_angelscript
{

class SetupError: public std::exception
{
public:
    SetupError(const char* msg): std::exception(msg) {}
};

/// @throws SetupException on error
void RegisterInterface(asIScriptEngine *engine);

} // namespace imgui_angelscript