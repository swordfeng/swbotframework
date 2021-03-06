from core import *
from core import _
import db
import logging
import telegram
import asyncio
import logging

logger = logging.getLogger('telegram')

def initialize():
    register_root(TelegramNS)

def finalize():
    unregister_root(TelegramNS)

class TelegramNS:
    bots = {}
    def ident():
        return 'telegram'
    def query(ids):
        if ids[0] == 'user':
            return TelegramUser.query(ids[1:])
        if ids[0] == 'message_type':
            return TelegramMessageType
        bot = _(f'telegram:{ids[0]}')
        return bot.query(ids[1:])
    def newbot(token):
        bot = TelegramBot(token)
        TelegramNS.bots[bot.bot_id] = bot
    def on_unregister_root():
        for bot_id in TelegramNS.bots:
            TelegramNS.bots[bot_id].kill()

@cacheable
class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token, request=telegram.utils.request.Request(con_pool_size=8))
        self.bot_id = self.token.split(':')[0]
        self._config = db.get_json(self.ident())
        if self._config is None:
            self._config = {}
        self.running = True
        self.task = asyncio.ensure_future(self.worker(), loop=event_loop)
    @property
    def last_update(self):
        if 'last_update' in self._config:
            return self._config['last_update']
        return 0
    @last_update.setter
    def last_update(self, value):
        self._config['last_update'] = value
        self.persist()
    def persist(self):
        db.put_json(self.ident(), self._config)
    def ident(self):
        return 'telegram:' + self.bot_id
    def query(self, ids):
        if ids[0] == 'chan':
            chat = self.bot.getChat(chat_id=ids[1])
            return TelegramChannel(chat, self)
        elif ids[0] == 'message':
            return _(Message.query_alias(join_ident(['telegram', self.bot_id, 'message', ids[1]])))
    def kill(self):
        self.running = False
        self.task.cancel()
    async def worker(self):
        while True:
            try:
                logger.debug('poll')
                updates = await async_execute(self.bot.getUpdates, offset=self.last_update)
                logger.debug('updates')
                for update in updates:
                    if update.update_id >= self.last_update:
                        self.last_update = update.update_id + 1
                    msg = telegram2message(update, self)
                    logger.debug(f'receive: {msg}')
                    if msg is not None:
                        chan = _(msg.origin)
                        chan.on_receive(msg)
            except telegram.error.TimedOut:
                logger.debug('poll timeout')
            except asyncio.CancelledError:
                break
            except:
                logger.exception('worker exception')

class TelegramChannel(Channel):
    def __init__(self, chat: telegram.Chat, bot: TelegramBot):
        self.bot = bot
        self.chat = chat
        self.chat_id = chat.id
        super().__init__() # load config, cache
    def ident(self):
        return f'{self.bot.ident()}:chan:{self.chat_id}'
    def send_message(self, msg: Message, chan: Channel):
        logger.debug(f'{self.ident()} send: {msg}')
        if msg.is_control:
            return
        if msg.text is not None:
            if len(msg.text) == 0:
                return
            kw = {'chat_id': self.chat_id, 'text': msg.text}
            if msg.user:
                kw['text'] = f'[{_(msg.user).display_name()}] {kw["text"]}'
            if msg.reply_to:
                rep_msg = query_object(msg.reply_to)
                ident = rep_msg.get_alias(f'telegram:{self.bot.bot_id}:message')
                if ident is not None:
                    kw['reply_to_message_id'] = int(split_ident(ident)[3])
            asyncio.ensure_future(self._send_message(msg, kw), loop=event_loop)
    async def _send_message(self, msg: Message, kw):
        _tm = await async_execute(self.bot.bot.sendMessage, **kw)
        msg.add_alias(f'telegram:{self.bot.bot_id}:message:{_tm.message_id}')

class TelegramUser(User):
    def query(ids):
        return TelegramUser(int(ids[0]))
    def __init__(self, uid, data=None):
        self.uid = uid
        if data is None:
            data = db.get_json(self.ident())
        if data is None:
            data = {}
        data['uid'] = uid
        self.data = data
        self.persist()
        super().__init__()
    def ident(self):
        return f'telegram:user:{self.uid}'
    def persist(self):
        db.put_json(self.ident(), self.data)
    def on_uncache(self):
        self.persist()
    def display_name(self):
        name = '<unknown>'
        if 'username' in self.data and self.data['username'] is not None:
            name = self.data['username']
        elif 'first_name' in self.data and self.data['first_name'] is not None:
            name = self.data['first_name']
        elif 'last_name' in self.data and self.data['last_name'] is not None:
            name = self.data['last_name']
        return name
    def info(self):
        return super().info() + '\n' + yamldump(self.data)
    def update(u: telegram.User):
        user = query_object(f'telegram:user:{u.id}')
        d = u.to_dict()
        if user is None:
            user = TelegramUser(u.id, d)
        else:
            if d != user.data:
                user.data = d
                user.persist()
        return user

class TelegramMessageType(BaseMessageType):
    def ident():
        return 'telegram:message_type'
    def text(self):
        if 'text' in self.content:
            return self.content['text']
        return None

def telegram2message(update: telegram.Update, bot: TelegramBot):
    if update.message:
        tm = update.message
        user = TelegramUser.update(tm.from_user)
        reply_to = None
        if tm.reply_to_message:
            reply_to = Message.query_alias(f'telegram:{bot.bot_id}:message:{tm.reply_to_message.message_id}')
        msg = Message.new(f'{bot.ident()}:chan:{tm.chat.id}', message_type=TelegramMessageType, user=user.ident(), content=tm.to_dict(), reply_to=reply_to)
        msg.add_alias(f'telegram:{bot.bot_id}:message:{tm.message_id}')
        return msg
    return None
