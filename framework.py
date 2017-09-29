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
        if 'to_listen' not in self.config:
            self.config['to_listen'] = []
        cache_object(self)
        for ident in self.config['listeners']:
            chan = query_object(ident)
            if chan is not None:
                self.add_listener(chan)
        for ident in self.config['to_listen']:
            chan = query_object(ident)
            if chan is not None:
                chan.add_listener(self)
    def add_listener(self, chan: 'Channel'):
        logger.info(f'{self.ident()} add_listener: {chan.ident()}')
        chanId = chan.ident()
        self.listeners[chanId] = chan
    def enable_listener(self, chan):
        chanId = chan.ident()
        logger.info(f'{self.ident()} enable_listener: {chan.ident()}')
        if chanId not in self.config['listeners']:
            self.config['listeners'].append(chanId)
            self.persist()
        if self.ident() not in chan.config['to_listen']:
            chan.config['to_listen'].append(self.ident())
            chan.persist()
    def remove_listener(self, chan: 'Channel'):
        logger.info(f'{self.ident()} remove_listener: {chan.ident()}')
        chanId = chan.ident()
        del(self.listeners[chanId])
    def disable_listener(self, chan):
        chanId = chan.ident()
        logger.info(f'{self.ident()} disable_listener: {chan.ident()}')
        if chanId in self.config['listeners']:
            self.config['listeners'].remove(chanId)
            self.persist()
        if self.ident() in self.config['to_listen']:
            chan.config['to_listen'].remove(self.ident())
            chan.persist()
    def on_receive(self, msg: 'Message'):
        logger.info(f'{self.ident()} on_receive: {msg}')
        for chanId in self.listeners:
            try:
                self.listeners[chanId].send_message(msg, self)
            except:
                logger.exception(f'Error sending message to {chanId}')
        glb = query_object('global_hook')
        if glb is not None:
            glb.send_message(msg, self)
    def on_uncache(self):
        self.persist()
    def persist(self):
        db.put_json(self.ident(), self.config)
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
            uuid = str(uuid1())
        self.uuid = uuid
        cache_object(self)
        self.persist()
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

