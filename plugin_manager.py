from importlib import *
import logging
import sys
import os
from util import *
from ns import *
import db
import plugins

#sys.path.append(os.path.dirname(os.path.realpath(__file__)))

logger = logging.getLogger('plugin_manager')

assert_plugin_name = assert_on_re('plugin name', r'^[A-Za-z0-9\-_]+$')

loaded_plugins = {}
enabled_plugins = db.get_json('pm')
if enabled_plugins is None:
    enabled_plugins = set()

def load_plugin(name):
    assert_plugin_name(name)
    if name in loaded_plugins:
        return
    try:
        mod = import_module(f'.{name}', 'plugins')
        mod.ident = lambda: f'pm.{name}'
        loaded_plugins[name] = mod
        reload(mod) # refresh module if changed
        mod.initialize()
    except:
        del(loaded_plugins[name])
        # todo: handle exception
        raise

def unload_plugin(name):
    assert_plugin_name(name)
    if name not in loaded_plugins:
        return
    try:
        mod = loaded_plugins[name]
        mod.finalize()
        del(loaded_plugins[name])
    except:
        del(loaded_plugins[name])
        # todo: handle exception
        raise

def reload_plugin(name):
    load(name)
    unload(name)

def list_plugin():
    return {'loaded': loaded_plugins.keys(), 'enabled': list(enabled_plugins)}

def enable_plugin(name: str):
    enabled_plugins.add(name)
    db.put_json(list(enabled_plugins))

def disable_plugin(name: str):
    enabled_plugins.discard(name)
    db.put_json(list(enabled_plugins))

class PluginManager:
    def ident():
        return 'pm'
    def query(ids):
        mod = loaded_plugins[ids[0]]
        if len(ids) == 1:
            return mod
        else:
            return mod.query(ids[1:])
    def load(name):
        return load_plugin(name)
    def unload(name):
        return unload_plugin(name)
    def reload(name):
        return reload_plugin(name)
    def enable(name):
        return enable_plugin(name)
    def disable(name):
        return disable_plugin(name)
    def list(name):
        return list_plugin(name)
register_root(PluginManager)

for plugin_name in enabled_plugins:
    load(plugin_name)

