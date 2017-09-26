import logging
from util import *
from ns import *
import plugin_manager
from uuid import uuid1
import db

logger = logging.getLogger('framework')

class Channel:
    def __init__(self):
        self.listeners = {}
        self.config = db.get_json(self.ident())
        if self.config is None:
            self.config = {}
        if 'listeners' not in self.config:
            self.config['listeners'] = []
        cache_object(self)
    def add_listener(self, chan: 'Channel'):
        chanId = chan.ident()
        if chanId not in self.config['listeners']:
            self.config['listeners'].append(chanId)
            self.persist()
        self.listeners[chanId] = chan
    def remove_listener(self, chan: 'Channel'):
        chanId = chan.ident()
        if chanId in self.config['listeners']:
            self.config['listeners'].remove(chanId)
            self.persist()
        del(self.listeners[chanId])
    def on_receive(self, msg: 'Message'):
        for chanId in self.listeners:
            try:
                self.listeners[chanId].send_message(msg, self)
            except:
                logger.exception(f'Error sending message to {chanId}')
    def on_uncache(self):
        self.persist()
    def persist(self):
        db.set_json(self.ident(), self.config)
    def ident(self):
        raise NotImplemented()
    def send_message(self, msg: 'Message', chan: 'Channel'):
        raise NotImplemented()

class Message(dict):
    '''
    Message is a json object with some helper functions.
    There are some important json properties that decides
    the content of the message.
    text: text content of the message
    origin: ident of origin channel
    user: ident of user
    reply_to: ident of user the message is replying to
    '''
    def query(ids):
        uuid = ids[0]
        data = db.get_json(uuid)
        return Message(data, uuid)

    def ident(self=None):
        if self is None:
            return 'message'
        return join_ident(['message', self.uuid])

    def __init__(self, data={}, uuid=None):
        super().__init__(data)
        if uuid == None:
            uuid = uuid1()
        self.uuid = uuid
        cache_object(self)
        self.persist()
    def on_uncache(self):
        self.persist()
    def persist(self):
        db.set_json(self.ident(), self.data)
    def add_alias(self, ident):
        assert_ident(ident)
        if 'alias' not in self:
            self['alias'] = []
        self['alias'].append()
        self.persist()
        db.set(ident, self.ident())
    def query_alias(alias):
        ident = db.get(alias)
        if ident is not None:
            return query_object(ident)
        return None
register_root(Message)

class User:
    def ident(self):
        raise NotImplemented()
    def display_name(self):
        raise NotImplemented()
    def avatar(self):
        raise NotImplemented()

