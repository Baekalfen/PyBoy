#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#

import importlib
import inspect
import logging
import os
import sys
import sysconfig
from pathlib import Path
from pkgutil import iter_modules

from pyboy import plugins
from pyboy.plugins.base_plugin import PyBoyDebugPlugin, PyBoyGameWrapper, PyBoyPlugin, PyBoyWindowPlugin

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata

logger = logging.getLogger(__name__)

EXT_SUFFIX = sysconfig.get_config_var("EXT_SUFFIX")

registered_plugins = []
registered_window_plugins = []
registered_gamewrappers = []

enabled_plugins = []
enabled_window_plugins = []
enabled_gamewrappers = []

builtin_plugins = [importlib.import_module("pyboy.plugins." + m.name) for m in iter_modules(plugins.__path__)]
external_plugins = []
for p in importlib_metadata.distributions():
    for e in p.entry_points:
        if e.group == "pyboy":
            external_plugins.append(e.load())

for mod in builtin_plugins + external_plugins:
    if hasattr(mod, "_export_plugins"):
        plugin_names = getattr(mod, "_export_plugins")
    else:
        plugin_names = [x for x in dir(mod) if not x.startswith("_")]

    for attr_name in plugin_names:
        _mod_class = getattr(mod, attr_name)
        if inspect.isclass(_mod_class) and issubclass(_mod_class, PyBoyPlugin) and _mod_class not in [
            PyBoyPlugin, PyBoyWindowPlugin, PyBoyGameWrapper, PyBoyDebugPlugin
        ]:
            if issubclass(_mod_class, PyBoyGameWrapper):
                registered_gamewrappers.append(_mod_class)
            elif issubclass(_mod_class, PyBoyWindowPlugin):
                registered_window_plugins.append(_mod_class)
            else:
                registered_plugins.append(_mod_class)


def parser_arguments():
    for p in registered_plugins + registered_window_plugins + registered_gamewrappers:
        yield p.argv


def window_names():
    for p in registered_window_plugins:
        if p.name:
            yield p.name


def external_plugin_names():
    return ", ".join([p.__name__ for p in external_plugins])


class PluginManager:
    def __init__(self, pyboy, mb, pyboy_argv):
        self.pyboy = pyboy

        if external_plugins:
            logger.info(f"External plugins loaded: {external_plugin_names()}")
        else:
            logger.info("No external plugins found")

        self.enabled_plugins = [p(pyboy, mb, pyboy_argv) for p in registered_plugins if p.enabled(pyboy, pyboy_argv)]
        self.enabled_window_plugins = [
            p(pyboy, mb, pyboy_argv) for p in registered_window_plugins if p.enabled(pyboy, pyboy_argv)
        ]
        self.enabled_debug_plugins = [p for p in self.enabled_window_plugins if isinstance(p, PyBoyDebugPlugin)]
        self.enabled_gamewrappers = [
            p(pyboy, mb, pyboy_argv) for p in registered_gamewrappers if p.enabled(pyboy, pyboy_argv)
        ]

        self.plugin_mapping = {}
        for p in self.enabled_window_plugins + self.enabled_plugins + self.enabled_gamewrappers:
            self.plugin_mapping[p.__class__.__name__] = p

    def list_plugins(self):
        return list(self.plugin_mapping.keys())

    def get_plugin(self, name):
        return self.plugin_mapping[name]

    def gamewrapper(self):
        if self.enabled_gamewrappers:
            # There should be exactly one enabled, if any.
            return self.enabled_gamewrappers[0]
        return None

    def handle_events(self, events):
        for p in self.enabled_window_plugins + self.enabled_plugins + self.enabled_gamewrappers:
            events = p.handle_events(events)
        return events

    def post_tick(self):
        for p in self.enabled_plugins + self.enabled_gamewrappers:
            p.post_tick()
        self._post_tick_windows()
        self._set_title()

    def _set_title(self):
        for p in self.enabled_window_plugins:
            p.set_title(self.pyboy.window_title)
        pass

    def _post_tick_windows(self):
        for p in self.enabled_window_plugins:
            p.post_tick()
        pass

    def frame_limiter(self, speed):
        if speed <= 0:
            return

        for p in self.enabled_window_plugins:
            if p.frame_limiter(speed):
                return

    def window_title(self):
        title = ""
        for p in self.enabled_window_plugins + self.enabled_plugins + self.enabled_gamewrappers:
            title += p.window_title()
        return title

    def stop(self):
        for p in self.enabled_window_plugins + self.enabled_plugins + self.enabled_gamewrappers:
            p.stop()
        pass

    def handle_breakpoint(self):
        for p in self.enabled_debug_plugins:
            p.handle_breakpoint()
        pass
