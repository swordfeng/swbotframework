from core import *

class Echo(Channel):
    def ident(self):
        return 'echo'
    def send_message(self, msg, chan):
        if msg.text is None:
            return
        rep = Message.new(self.ident(), reply_to=msg.ident(), text=msg.text)
        chan.send_message(rep, self)

def initialize():
    echo = Echo()
    register_root(echo)

def finalize():
    echo = query_object('echo')
    unregister_root(echo)
