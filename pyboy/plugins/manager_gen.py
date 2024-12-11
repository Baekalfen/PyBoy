#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import importlib
import importlib.util
import os
import re
import sys

# Makes us able to import PyBoy from the directory below
file_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, file_path + "/../..")

# Plugins and priority!
# E.g. DisableInput first
windows = ["WindowSDL2", "WindowOpenGL", "WindowNull", "Debug"]
game_wrappers = [
    "GameWrapperSuperMarioLand",
    "GameWrapperTetris",
    "GameWrapperKirbyDreamLand",
    "GameWrapperPokemonGen1",
    "GameWrapperPokemonPinball",
]
plugins = [
    "AutoPause",
    "RecordReplay",
    "Rewind",
    "ScreenRecorder",
    "ScreenshotRecorder",
    "DebugPrompt",
] + game_wrappers
all_plugins = windows + plugins


def to_snake_case(s):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def skip_lines(iterator, stop):
    # Skip old lines
    while True:
        if next(line_iter).strip().startswith(stop):
            break


if __name__ == "__main__":
    out_lines = []
    with open("manager.py", "r") as f:
        line_iter = iter(f.readlines())
        while True:
            line = next(line_iter, None)
            if line is None:
                break

            # Find place to inject
            if line.strip().startswith("# foreach"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# foreach")

                skip_lines(line_iter, "# foreach end")

                _, foreach, plugin_type, fun = line.strip().split(" ", 3)
                for p in eval(plugin_type):
                    p_name = to_snake_case(p)
                    lines.append(f"if self.{p_name}_enabled:\n")
                    # lines.append(f"    {var_name} = self.{p_name}\n")
                    for sub_fun in fun.split(", "):
                        sub_fun = sub_fun.replace("[]", f"self.{p_name}")
                        lines.append(f"    {sub_fun}\n")

                lines.append("# foreach end\n")
                out_lines.extend([indentation + l for l in lines])
            elif line.strip().startswith("# plugins_enabled"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# plugins_enabled")

                skip_lines(line_iter, "# plugins_enabled end")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"self.{p_name} = {p}(pyboy, mb, pyboy_argv)\n")
                    lines.append(f"self.{p_name}_enabled = self.{p_name}.enabled()\n")

                lines.append("# plugins_enabled end\n")
                out_lines.extend([indentation + l for l in lines])
            elif line.strip().startswith("# yield_plugins"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# yield_plugins")

                skip_lines(line_iter, "# yield_plugins end")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"yield {p}.argv\n")

                lines.append("# yield_plugins end\n")
                out_lines.extend([indentation + l for l in lines])
            elif line.strip().startswith("# imports"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# imports")

                skip_lines(line_iter, "# imports end")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"from pyboy.plugins.{p_name} import {p} # noqa\n")

                lines.append("# imports end\n")
                out_lines.extend([indentation + l for l in lines])
            elif line.strip().startswith("# gamewrapper"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# gamewrapper")

                skip_lines(line_iter, "# gamewrapper end")

                for p in game_wrappers:
                    p_name = to_snake_case(p)
                    lines.append(f"if self.{p_name}_enabled: return self.{p_name}\n")

                lines.append("# gamewrapper end\n")
                out_lines.extend([indentation + l for l in lines])
            else:
                out_lines.append(line)

    with open("manager.py", "w") as f:
        f.writelines(out_lines)

    out_lines = []
    with open("manager.pxd", "r") as f:
        line_iter = iter(f.readlines())
        while True:
            line = next(line_iter, None)
            if line is None:
                break

            # Find place to inject
            if line.strip().startswith("# plugin_cdef"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# plugin_cdef")

                skip_lines(line_iter, "# plugin_cdef end")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"cdef public {p} {p_name}\n")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"cdef bint {p_name}_enabled\n")

                lines.append("# plugin_cdef end\n")
                out_lines.extend([indentation + l for l in lines])
            elif line.strip().startswith("# imports"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# imports")

                skip_lines(line_iter, "# imports end")

                for p in all_plugins:
                    p_name = to_snake_case(p)
                    lines.append(f"from pyboy.plugins.{p_name} cimport {p}\n")

                lines.append("# imports end\n")
                out_lines.extend([indentation + l for l in lines])
            else:
                out_lines.append(line)

    with open("manager.pxd", "w") as f:
        f.writelines(out_lines)

    out_lines = []
    with open("__init__.py", "r") as f:
        line_iter = iter(f.readlines())
        while True:
            line = next(line_iter, None)
            if line is None:
                break

            # Find place to inject
            if line.strip().startswith("# docs exclude"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("# docs exclude")

                skip_lines(line_iter, "# docs exclude end")

                for p in sorted(list((set(all_plugins) - set(game_wrappers)) | set(["manager", "manager_gen"]))):
                    p_name = to_snake_case(p)
                    lines.append(f'"{p_name}": False,\n')

                lines.append("# docs exclude end\n")
                out_lines.extend([indentation + l for l in lines])
            else:
                out_lines.append(line)

    with open("__init__.py", "w") as f:
        f.writelines(out_lines)

    out_lines = []
    with open("../pyboy.py", "r") as f:
        line_iter = iter(f.readlines())
        while True:
            line = next(line_iter, None)
            if line is None:
                break

            # Find place to inject
            if line.strip().startswith("## Plugin kwargs:"):
                lines = [line.strip() + "\n"]
                indentation = " " * line.index("## Plugin kwargs:")

                skip_lines(line_iter, "Other keyword arguments may exist")

                for p in sorted(list(set(plugins) - set(game_wrappers))):
                    p_name = to_snake_case(p)
                    spec = importlib.util.spec_from_file_location(
                        p_name, os.path.dirname(os.path.abspath(__file__)) + "/" + p_name + ".py"
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr in dir(module):
                        if attr.startswith("_") or attr == "PyBoyPlugin":
                            continue
                        _plugin = getattr(module, attr)
                        if getattr(_plugin, "__bases__", None) and _plugin.__bases__[0].__name__ == "PyBoyPlugin":
                            for argv in _plugin.argv:
                                name, argv_desc = argv
                                name = name.strip("-").replace("-", "_")
                                _type = argv_desc.get("type", str).__name__
                                if argv_desc.get("action") == "store_true":
                                    _type = "bool"
                                _help = argv_desc.get("help")
                                if not _help:
                                    print("Missing documentation", p_name, argv)
                                    continue
                                lines.append(f"* {name} ({_type}): {_help} [plugin: {p}]\n")
                    del spec, module

                lines.append(
                    "Other keyword arguments may exist for plugins that are not listed here. They can be viewed by running `pyboy --help` in the terminal.\n"
                )
                out_lines.extend([indentation + l for l in lines])
                out_lines.insert(-1, "\n")  # Avoids whitespace
            else:
                out_lines.append(line)

    with open("../pyboy.py", "w") as f:
        f.writelines(out_lines)
