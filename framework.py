import logging
from util import *
from ns import *
from ns import _
import plugin_manager
from uuid import uuid1
import db

logger = logging.getLogger('framework')

@cacheable
class Channel:
    def __init__(self):
        self.config = db.get_json(self.ident())
        if self.config is None:
            self.config = {}
        if 'listeners' not in self.config:
            self.config['listeners'] = []
        if 'listen_to' not in self.config:
            self.config['listen_to'] = []
    def add_listener(self, chan: 'Channel'):
        logger.info(f'{self.ident()} add_listener: {chan.ident()}')
        chanId = chan.ident()
        if chanId not in self.config['listeners']:
            self.config['listeners'].append(chanId)
            self.persist()
        if self.ident() not in chan.config['listen_to']:
            chan.config['listen_to'].append(self.ident())
            chan.persist()
    def remove_listener(self, chan: 'Channel'):
        logger.info(f'{self.ident()} remove_listener: {chan.ident()}')
        chanId = chan.ident()
        if chanId in self.config['listeners']:
            self.config['listeners'].remove(chanId)
            self.persist()
        if self.ident() in chan.config['listen_to']:
            chan.config['listen_to'].remove(self.ident())
            chan.persist()
    def on_receive(self, msg: 'Message'):
        logger.debug(f'{self.ident()} on_receive: {msg}')
        for chanId in list(self.config['listeners']):
            try:
                chan = query_object(chanId)
                if chan is not None:
                    chan.send_message(msg, self)
            except:
                logger.exception(f'Error sending message to {chanId}')
        global_hook = query_object('global_hook')
        if global_hook is not None:
            global_hook.send_message(msg, self)
    def on_uncache(self):
        self.persist()
    def persist(self):
        db.put_json(self.ident(), self.config)
    def ident(self):
        raise NotImplemented()
    def send_message(self, msg: 'Message', chan: 'Channel'):
        raise NotImplemented()
    def info(self):
        return yamldump(self.config)

class BaseMessageType:
    def ident():
        raise NotImplementedError
    def origin(self):
        return self['origin']
    def reply_to(self):
        if 'reply_to' in self and type(self['reply_to']) is str:
            return self['reply_to']
        return None
    def user(self):
        if 'user' in self and type(self['user']) is str:
            return self['user']
        return None
    def content(self):
        return self['content']
    def is_control(self): # override
        return False
    def text(self): # override
        return None
class GeneralTextMessageType(BaseMessageType):
    def ident():
        return 'message_type_general_text'
    def text(self):
        if 'text' not in self.content:
            return None
        return self.content['text']
register_root(GeneralTextMessageType)

@cacheable
class Message(dict):
    '''
    Message is a json object with some helper functions.
    There are some important json properties that decides
    the content of the message.
    type: ident of message type
    content: content of the message -- based on message type
        .text: text content  -- this is the default of base message type
    origin: ident of origin channel
    user: ident of user
    reply_to: ident of user the message is replying to
    '''
    def query(ids):
        uuid = ids[0]
        data = db.get_json(join_ident(['message', uuid]))
        return Message(data, uuid)

    def ident(self=None):
        if self is None:
            return 'message'
        return join_ident(['message', self.uuid])

    def new(origin, reply_to=None, user=None, message_type=GeneralTextMessageType, **content):
        assert_ident(origin)
        if 'content' in content:
            content = content['content']
        data = {
            'type': message_type.ident(),
            'origin': origin,
            'content': content
        }
        if reply_to is not None:
            assert_ident(reply_to)
            data['reply_to'] = reply_to
        if user is not None:
            assert_ident(user)
            data['user'] = user
        msg = Message(data)
        msg.persist()
        return msg

    def __init__(self, data={}, uuid=None):
        super().__init__(data)
        if uuid is None:
            uuid = str(uuid1())
        self.uuid = uuid
        self.message_type = _(self['type'])
    def __getattr__(self, name):
        if hasattr(self.message_type, name):
            return getattr(self.message_type, name)(self)
        raise AttributeError
    def on_uncache(self):
        self.persist()
    def persist(self):
        db.put_json(self.ident(), self)
    def add_alias(self, ident):
        assert_ident(ident)
        if 'alias' not in self:
            self['alias'] = []
        self['alias'].append(ident)
        self.persist()
        db.put(ident, self.ident())
    def get_alias(self, prefix):
        assert_ident(prefix)
        if 'alias' not in self:
            return None
        for ident in self['alias']:
            if ident == prefix or (ident.startswith(prefix) and ident[len(prefix)] == ':'):
                return ident
        return None
    def query_alias(alias):
        ident = db.get(alias)
        return ident
    def info(self):
        i = dict(self)
        i['content'] = '<hidden>'
        return yamldump(i)
register_root(Message)

@cacheable
class User:
    def ident(self):
        raise NotImplemented()
    def display_name(self):
        raise NotImplemented()
    def avatar(self):
        raise NotImplemented()
    def info(self):
        return f'Display Name: {self.display_name()}'

