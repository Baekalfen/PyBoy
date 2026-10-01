"""Sphinx configuration for the PyBoy documentation."""

from pathlib import Path
import re
import sys


DOCS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DOCS_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

project = "PyBoy"
copyright = "2026, Mads Ynddal"
author = "Mads Ynddal"
release = "2.7.1"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_member_order = "bysource"
autodoc_preserve_defaults = True
autodoc_typehints = "none"
autodoc_default_options = {
    "no-value": True,
}
# Keep the source docstrings in their existing Markdown form for pytest, and
# adapt their presentation only in the copy Sphinx passes to this handler.
suppress_warnings = ["ref.python"]

_INTERNAL_REFERENCE_PREFIXES = (
    "pyboy.PyBoy",
    "pyboy.PyBoyMemoryView",
    "pyboy.PyBoyRegisterFile",
    "pyboy.api.",
    "pyboy.utils.",
    "pyboy.plugins.base_plugin.",
    "pyboy.plugins.game_wrapper_",
)
_UNQUALIFIED_REFERENCE_PREFIXES = {
    "PyBoy": "pyboy.PyBoy",
    "PyBoyMemoryView": "pyboy.PyBoyMemoryView",
    "PyBoyRegisterFile": "pyboy.PyBoyRegisterFile",
    "Sprite": "pyboy.api.sprite.Sprite",
    "Tile": "pyboy.api.tile.Tile",
    "TileMap": "pyboy.api.tilemap.TileMap",
    "Screen": "pyboy.api.screen.Screen",
    "Sound": "pyboy.api.sound.Sound",
}
_UNQUALIFIED_REFERENCE_TARGETS = {
    "game_area": "pyboy.plugins.base_plugin.PyBoyGameWrapper.game_area",
    "reset_game": "pyboy.plugins.base_plugin.PyBoyGameWrapper.reset_game",
    "start_game": "pyboy.plugins.base_plugin.PyBoyGameWrapper.start_game",
    "set_badge": "pyboy.plugins.game_wrapper_pokemon_gen1.GameWrapperPokemonGen1.set_badge",
    "rtc_lock_experimental": "pyboy.PyBoy.rtc_lock_experimental",
}
_ATTRIBUTE_REFERENCE_TARGETS = {
    "pyboy.PyBoy.game_wrapper",
    "pyboy.PyBoy.memory",
    "pyboy.PyBoy.memory_scanner",
    "pyboy.PyBoy.register_file",
    "pyboy.PyBoy.tilemap_background",
    "pyboy.PyBoy.tilemap_window",
    "pyboy.api.sound.Sound.raw_buffer_format",
    "pyboy.api.sprite.Sprite.tile_identifier",
    "pyboy.api.sprite.Sprite.tiles",
    "pyboy.api.tile.Tile.raw_buffer_format",
}
_REFERENCE_ALIASES = {
    "pyboy.plugins": "plugins-reference",
    "pyboy.api": "api-reference",
    "pyboy.memory": "pyboy.PyBoy.memory",
    "pyboy.screen": "pyboy.PyBoy.screen",
    "pyboy.tilemap_background": "pyboy.PyBoy.tilemap_background",
    "pyboy.tilemap_window": "pyboy.PyBoy.tilemap_window",
    "pyboy.plugins.manager.PluginManager": "plugins-reference",
    "pyboy.sprite_by_tile_identifier": "pyboy.PyBoy.get_sprite_by_tile_identifier",
}
_EXTERNAL_REFERENCE_TARGETS = {
    "False": ("obj", "False"),
    "None": ("obj", "None"),
    "PIL.Image": ("class", "PIL.Image.Image"),
    "True": ("obj", "True"),
    "int": ("class", "int"),
    "memoryview": ("class", "memoryview"),
    "ndarray": ("class", "numpy.ndarray"),
    "numpy.ndarray": ("class", "numpy.ndarray"),
    "print": ("func", "print"),
    "str": ("class", "str"),
}
_EXTERNAL_REFERENCE_URLS = {
    "numpy.uint8": "https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.uint8",
    "seek": "https://docs.python.org/3/library/io.html#io.IOBase.seek",
}
_GAME_WRAPPER_CLASSES = {
    "GameWrapperSuperMarioLand": "pyboy.plugins.game_wrapper_super_mario_land.GameWrapperSuperMarioLand",
}


def _internal_reference(value):
    """Return an RST cross-reference for a documented PyBoy object."""
    if value in _EXTERNAL_REFERENCE_TARGETS:
        role, target = _EXTERNAL_REFERENCE_TARGETS[value]
        return f":{role}:`{value} <{target}>`"

    if value in _EXTERNAL_REFERENCE_URLS:
        return f"`{value} <{_EXTERNAL_REFERENCE_URLS[value]}>`_"

    if value.startswith("pyboy.memory["):
        return f":attr:`{value} <pyboy.PyBoy.memory>`"

    if value.startswith("tilemap["):
        return f":class:`{value} <pyboy.api.tilemap.TileMap>`"

    if value.startswith("PyBoy("):
        return f":class:`{value} <pyboy.PyBoy>`"

    lookup_value = value[:-2] if value.endswith("()") else value
    if lookup_value == "__getitem__":
        return f":class:`{value} <pyboy.api.tilemap.TileMap>`"

    if lookup_value in _REFERENCE_ALIASES:
        target = _REFERENCE_ALIASES[lookup_value]
        if target in {"api-reference", "plugins-reference"}:
            label = "Hardware API" if target == "api-reference" else "Plugins"
            return f":ref:`{label} <{target}>`"
        return f":any:`{value} <{target}>`"

    if lookup_value in _UNQUALIFIED_REFERENCE_TARGETS:
        target = _UNQUALIFIED_REFERENCE_TARGETS[lookup_value]
        return f":any:`{value} <{target}>`"

    target = lookup_value
    if lookup_value in {"PyBoy", "PyBoyMemoryView", "PyBoyRegisterFile"}:
        target = f"pyboy.{lookup_value}"
    elif re.fullmatch(r"PyBoy\.[A-Za-z_]\w*", lookup_value):
        target = f"pyboy.{lookup_value}"
    else:
        for prefix, qualified_prefix in _UNQUALIFIED_REFERENCE_PREFIXES.items():
            if lookup_value == prefix or re.fullmatch(rf"{prefix}\.[A-Za-z_]\w*", lookup_value):
                target = lookup_value.replace(prefix, qualified_prefix, 1)
                break
        else:
            for prefix, qualified_prefix in _GAME_WRAPPER_CLASSES.items():
                if lookup_value.startswith(f"{prefix}."):
                    target = lookup_value.replace(prefix, qualified_prefix, 1)
                    break
            else:
                target = lookup_value
    if target == lookup_value and not lookup_value.startswith(_INTERNAL_REFERENCE_PREFIXES):
        return None

    if not re.fullmatch(r"pyboy\.[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", target):
        return None
    role = "attr" if target in _ATTRIBUTE_REFERENCE_TARGETS else "any"
    return f":{role}:`{value} <{target}>`"


def _convert_inline_code(match):
    value = match.group(1)
    return _internal_reference(value) or f"``{value}``"


def _markdown_docstring_to_rst(app, what, name, obj, options, lines):  # pylint: disable=unused-argument
    """Convert the Markdown constructs used by PyBoy's docstrings to RST."""
    converted = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                converted.append("")
            else:
                if converted and converted[-1]:
                    converted.append("")
                language = stripped[3:].strip() or "text"
                converted.extend((f".. code-block:: {language}", ""))
                in_code_block = True
            continue

        if in_code_block:
            converted.append(f"   {line}" if line else "")
            continue

        if stripped and set(stripped) == {"#"}:
            continue

        heading = re.match(r"^(#+)\s+(.+)$", stripped)
        if heading:
            title = heading.group(2)
            converted.extend((title, "~" * len(title), ""))
            continue

        image = re.match(r"^!\[([^]]+)\]\(([^)]+)\)$", stripped)
        if image:
            if converted and converted[-1]:
                converted.append("")
            converted.extend(
                (
                    f".. image:: {image.group(2)}",
                    f"   :alt: {image.group(1)}",
                    "",
                )
            )
            continue

        line = re.sub(r"__NOTE(?::)?__[:]?", "**NOTE:**", line)
        line = re.sub(r"(?<!`)``([^`\n]+)``(?!`)", _convert_inline_code, line)
        line = re.sub(r"(?<![:`])`([^`\n]+)`(?!`)", _convert_inline_code, line)
        # Add spacing only after a complete literal, not across adjacent delimiters.
        line = re.sub(r"(?<!\w)(``[^`\n]+``)(?=\w)", r"\1 ", line)
        line = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"`\1 <\2>`_", line)
        converted.append(line)

    lines[:] = converted


intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable/", None),
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "docs"]
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

html_theme = "furo"
html_title = "PyBoy documentation"
html_extra_path = ["CNAME"]
html_static_path = []
html_theme_options = {
    "footer_icons": [
        {
            "name": "PyBoy on GitHub",
            "url": "https://github.com/Baekalfen/PyBoy",
            "html": (
                "<span>PyBoy on GitHub</span>&nbsp;"
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" '
                'viewBox="0 0 16 16" aria-hidden="true">'
                '<path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 '
                "2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49"
                "-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15"
                "-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 "
                "2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 "
                "0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 "
                "2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 "
                "2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 "
                "2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 "
                "1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 "
                '16 8c0-4.42-3.58-8-8-8z"></path></svg>'
            ),
        }
    ],
}


def setup(app):
    app.connect("autodoc-process-docstring", _markdown_docstring_to_rst)
