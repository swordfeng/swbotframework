from core import *

class Echo(Channel):
    def ident(self):
        return 'echo'
    def send_message(self, msg, chan):
        if 'content' not in msg:
            return
        if msg['origin'] == self.ident():
            return
        if msg['origin'] != chan.ident():
            return
        rep = Message({
            'content': msg['content'],
            'origin': self.ident(),
            'reply_to': msg.ident()
            })
        chan.send_message(rep, self)

def initialize():
    echo = Echo()
    register_root(echo)

def finalize():
    echo = query_object('echo')
    unregister_root(echo)
