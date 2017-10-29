from core import *
from core import _
import logging

logger = logging.getLogger('simple_manager')

class SimpleManager(Channel):
    def ident(self):
        return 'simple_manager'
    def send_message(self, msg, chan):
        if 'content' not in msg or 'text' not in msg['content'] or msg['origin'] != chan.ident():
            return
        cmd = msg['content']['text']
        if not cmd.startswith('sm:'):
            return
        cmd = cmd[3:].strip()
        result = handle(cmd, msg, chan)
        rep = Message({
            'content': {
                'text': result
                },
            'reply_to': msg.ident(),
            'origin': self.ident()
            })
        chan.send_message(rep, chan)
    def on_register_root(self):
        query_object('global_hook').add_listener(self)
    def on_unregister_root(self):
        query_object('global_hook').remove_listener(self)

def handle(cmd, msg, chan):
    cmds = cmd.split(' ')
    if len(cmds) == 0:
        return 'Command required'
    if cmds[0] == 'info':
        item = None
        if len(cmds) > 1:
            item = cmds[1]
        else:
            item = msg.ident()
        obj = query_object(item)
        if obj is None:
            return 'Object not found'
        return get_info(obj)
    return 'Unrecognized command'

def get_info(obj):
    klass = type(obj)
    cname = f'{klass.__module__}.{klass.__name__}'
    info = f'ID: {obj.ident()}\nType: {cname}'
    if klass is type:
        name = f'{obj.__module__}.{obj.__name__}'
        info += f'\nName: {name}'
    try:
        if hasattr(obj, 'info'):
            moreinfo = obj.info()
            info += '\n'
            info += moreinfo
    except:
        logger.exception(f'Bad info()')
    return info

def initialize():
    register_root(SimpleManager())
    
def finalize():
    unregister_root(_('simple_manager'))
