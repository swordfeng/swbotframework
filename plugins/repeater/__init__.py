from core import *
from core import _

class Repeater(Channel):
    def __init__(self):
        super().__init__()
        self.last_msgs = {}
    def ident(self):
        return 'repeater'
    def send_message(self, msg, chan):
        if 'content' not in msg or 'text' not in msg['content'] or msg['origin'] != chan.ident():
            return
        ident = chan.ident()
        text = msg['content']['text']
        if ident not in self.last_msgs:
            self.last_msgs[ident] = {'last': '', 'count': 0}
        item = self.last_msgs[ident]
        if text != item['last']:
            item['last'] = text
            item['count'] = 1
        else:
            item['count'] += 1
        if item['count'] == 3:
            resp = Message({
                'content': {
                    'text': text
                    },
                'origin': self.ident()
                })
            chan.send_message(resp, self)

def initialize():
    register_root(Repeater())
def finalize():
    unregister_root(_('repeater'))
