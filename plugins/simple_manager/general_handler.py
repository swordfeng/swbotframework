from core import *
import logging

class GeneralHandler(Channel):
    def __init__(self):
        assert_name(self.name)
        assert(type(self.prompt) == str)
        if not hasattr(self, 'description'):
            self.description = self.name
        self.logger = logging.getLogger(self.name)
        self.handlers = {}
        self.helpmsg = {}
        handler(self.help, target=self, helpmsg='Show help')
        super().__init__(self)
    def ident(self):
        return self.name
    def send_message(self, msg, chan):
        if 'content' not in msg or 'text' not in msg['content'] or msg['origin'] != chan.ident():
            return
        cmd = msg['content']['text']
        if not cmd.startswith(self.prompt):
            return
        cmds = cmd[len(self.prompt):].strip().split(' ')
        try:
            result = self.handle(cmds, msg, chan)
        except:
            self.logger.info(f'Unhandled command: {cmd}', exc_info=True)
            result = 'Error happened when processing the command'
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
    def handle(self, cmds, msg, chan):
        if cmds[0] not in self.handlers:
            return f'Command {cmds[0]} not found'
        return self.handlers[cmds[0]](cmds[1:], msg, chan)
    def help(self):
        result = self.description
        for cmd in self.helpmsg:
            result += f'{cmd}: {self.helpmsg[cmd]}'
        return result

def handler(func, target=None, name=None, helpmsg='No help'):
    assert(isinstance(target, GeneralHandler))
    if name is None:
        name = func.__name__
    target.handlers[name] = func
    target.helpmsg[name] = helpmsg
    return func