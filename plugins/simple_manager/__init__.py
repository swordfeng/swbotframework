from core import *

class SimpleManager(Channel):
    def ident(self):
        return 'simple_manager'
    def send_message(self, msg, chan):
        if 'content' not in msg:
            return
        if 'text' not in msg['content']:
            return
        if msg['origin'] != chan.ident():
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

def handle(cmd, msg, chan):
    cmds = cmd.split(' ')
    if cmds[0] == 'info':
        result = ''
        if 'user' in msg and msg['user'] is not None:
            user = query_object(msg['user'])
            result += f'User ID: {user.ident()}\nUser Name: {user.display_name()}\n'
        result += f'Origin Channel: {msg["origin"]}\nDirect Channel: {chan.ident()}\n'
        result += f'Message ID: {msg.ident()}\nMessage: {msg}'
        return result
    return 'unrecognized command'


def initialize():
    sm = SimpleManager()
    register_root(sm)
    query_object('global_hook').add_listener(sm)
def finalize():
    sm = query_object('simple_manager')
    query_object('global_hook').remove_listener(sm)
    unregister_root(sm)
