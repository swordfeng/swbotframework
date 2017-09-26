from importlib import *
import logging
import sys
import os
from util import *
from ns import *
import plugins

#sys.path.append(os.path.dirname(os.path.realpath(__file__)))

logger = logging.getLogger('plugin_manager')

loaded_plugins = {}

assert_plugin_name = assert_on_re('plugin name', r'^[A-Za-z0-9\-_]+$')

def load_plugin(name: str):
    assert_plugin_name(name)
    if name in loaded_plugins:
        mod = loaded_plugins[name]
        try:
            mod.finalize()
        except:
            logger.exception(f'Error raised while unloading {name}')
    else:
        mod = import_module(f'.{name}', 'plugins')
        loaded_plugins[name] = mod
    try:
        reload(mod) # refresh module if changed
        mod.initialize()
    except:
        del(loaded_plugins[name])
        # todo: handle exception (disable&restart program?)
        raise

def unload_plugin(name: str):
    assert_plugin_name(name)
    if name in loaded_plugins:
        mod = loaded_plugins[name]
        mod.finalize()
        del(loaded_plugins[name])

def list_plugin():
    pass

def enable_plugin(name: str):
    pass

def disable_plugin(name: str):
    pass


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
        load_plugin(name)
    def unload(name):
        unload_plugin(name)
register_root(PluginManager)
