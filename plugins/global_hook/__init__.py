from core import *
from core import _
import logging

logger = logging.getLogger('global_hook')

class GlobalHook(Channel):
    def ident(self):
        return 'global_hook'
    def send_message(self, msg, chan):
        if chan.ident() == self.ident():
            return
        for chanId in list(self.config['listeners']):
            try:
                _(chanId).send_message(msg, chan)
            except:
                logger.exception(f'Error sending message to {chanId}')

def initialize():
    register_root(GlobalHook())
def finalize():
    unregister_root(query_object('global_hook'))
