from core import *
from core import _
import logging
from .general_handler import *
from .perm import PermissionNS

logger = logging.getLogger('simple_manager')

class SimpleManager(GeneralHandler):
    def __init__(self):
        super().__init__()
        self.register(info, helpmsg='Show some information about an object')
    name = 'simple_manager'
    prompt = 'sm:'
    description = '''Simple Manager
developed by swordfeng
Home: https://github.com/swordfeng/swbotframework/tree/master/plugins/simple_manager'''

def info(cmds, msg, chan):
    item = None
    if len(cmds) > 0:
        item = cmds[0]
    else:
        item = msg.ident()
    obj = query_object(item)
    if obj is None:
        return 'Object not found'
    return get_info(obj)

def get_info(obj):
    klass = type(obj)
    cname = f'{klass.__module__}.{klass.__name__}'
    info = f'ID: {obj.ident()}\nType: {cname}'
    if klass is type:
        name = f'{obj.__module__}.{obj.__name__}'
        info += f'\nName: {name}'
    if hasattr(obj, 'info'):
        moreinfo = obj.info()
        info += '\n'
        info += moreinfo
    return info

def initialize():
    register_root(SimpleManager())
    register_root(PermissionNS())
    if query_object(f'permission:SuperUser') is None:
        PermissionNS.exec('addrole SuperUser')
        PermissionNS.exec('assign SuperUser to telegram:user:109890321')        
    
def finalize():
    unregister_root(_(SimpleManager.name))
    unregister_root(_(PermissionNS.name))
