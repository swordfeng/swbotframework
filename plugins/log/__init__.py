from core import *
from core import _
import logging

levels = ['INFO', 'WARN', 'ERROR']

class LogNS:
    def __init__(self):
        for level in levels:
            LogChannel(level)
    def ident(self):
        return 'log'

class LogHandler(logging.Handler):
    def __init__(self, cb):
        self.cb = cb
    def emit(self, record):
        self.cb(self.format(record))

class LogChannel(Channel):
    def __init__(self, level):
        self.level = level
        self.handler = LogHandler(self.on_log)
        self.handler.setLevel(getattr(logging, level))
        super().__init__()
        logging.getLogger().addHandler(self.handler)
    def ident(self):
        return f'log:{self.level}'
    def kill(self):
        logging.getLogger().removeHandler(self.handler)
    def on_log(self, log):
        log_msg = Message({
            'content': {'text': log},
            'origin': self.ident()
        })
    def send_message(self, msg, chan):
        return