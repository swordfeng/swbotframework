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
        super().__init__()
        self.register(self.help, helpmsg='Show help')
    def ident(self):
        return self.name
    def send_message(self, msg, chan):
        if 'content' not in msg or 'text' not in msg['content'] or msg['origin'] != chan.ident():
            return
        cmd = msg['content']['text']
        if not cmd.startswith(self.prompt):
            return
        cmds = cmd[len(self.prompt):].strip().split(' ')
        if len(cmds) == 0:
            result = 'Command required'
        else:
            try:
                result = self.handle(cmds, msg, chan)
            except PermissionError as e:
                result = f'Permission denied: {e}'
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
        chan.send_message(rep, self)
    def on_register_root(self):
        query_object('global_hook').add_listener(self)
    def on_unregister_root(self):
        query_object('global_hook').remove_listener(self)
    def handle(self, cmds, msg, chan):
        if cmds[0] not in self.handlers:
            return f'Command {cmds[0]} not found'
        return self.handlers[cmds[0]](cmds[1:], msg, chan)
    def help(self, cmds, msg, chan):
        result = self.description + '\nCommands:'
        for cmd in self.helpmsg:
            result += f'\n- {cmd}: {self.helpmsg[cmd]}'
        return result
    def register(self, func, name=None, helpmsg='No help'):
        if name is None:
            name = func.__name__
        self.handlers[name] = func
        self.helpmsg[name] = helpmsg
        return self
