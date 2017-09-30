from core import *
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
        if len(ids) < 2:
            raise Exception('not found')
        if ids[0] == 'user':
            return TelegramUser.query(ids[1:])
        bot = query_object(f'telegram:{ids[0]}')
        return bot.query(ids[1:])
    def newbot(token):
        bot = TelegramBot(token)
        TelegramNS.bots[bot.bot_id] = bot

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token)
        self.bot_id = self.token.split(':')[0]
        self.last_update = 0
        self.task = asyncio.ensure_future(self.worker(), loop=event_loop)
        cache_object(self)
    def ident(self):
        return 'telegram:' + self.bot_id
    def query(self, ids):
        if ids[0] == 'chan':
            chat = self.bot.getChat(chat_id=ids[1])
            return TelegramChannel(chat, self)
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
                    logger.info(f'receive: {msg}')
                    if msg is not None:
                        chan = query_object(msg['origin'])
                        chan.on_receive(msg)
            except telegram.error.TimedOut:
                logger.info('poll timeout')
            except:
                logger.exception('worker exception')
    def info(self):
        return f'Type: telegram bot\nID: {self.ident()}'

class TelegramChannel(Channel):
    def __init__(self, chat: telegram.Chat, bot: TelegramBot):
        self.bot = bot
        self.chat = chat
        self.chat_id = chat.id
        super().__init__() # load config, cache
    def ident(self):
        return f'{self.bot.ident()}:chan:{self.chat_id}'
    def send_message(self, msg: Message, chan: Channel):
        logger.info(f'{self.ident()} send: {msg}')
        if 'content' not in msg:
            # non-chat message
            return
        if 'file' in msg['content']:
            pass # todo: senddocuemnt
        elif 'image' in msg['content']:
            pass # todo: sendphoto
        elif 'text' in msg['content']:
            if len(msg['content']['text']) == 0:
                return
            kw = {'chat_id': self.chat_id, 'text': msg['content']['text']}
            if 'reply_to' in msg:
                rep_msg = query_object(msg['reply_to'])
                ident = rep_msg.get_alias(f'telegram:{self.bot.bot_id}:message')
                if ident is not None:
                    kw['reply_to_message_id'] = int(split_ident(ident)[3])
            self.bot.bot.sendMessage(**kw)
        else:
            logger.warning(f'ignored message: {msg}')
    def info(self):
        return super().info() + f'\nBot: {self.bot.ident()}'

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
        cache_object(self)
        self.persist()
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
        i = super().info()
        if 'username' in self.data and self.data['username'] is not None:
            i += '\nUsername: ' + self.data['username']
        elif 'first_name' in self.data and self.data['first_name'] is not None:
            i += '\nFirst Name: ' + self.data['first_name']
        elif 'last_name' in self.data and self.data['last_name'] is not None:
            i += '\nLast Name: ' + self.data['last_name']
        return i

def telegram2message(update: telegram.Update, bot: TelegramBot):
    if update.message:
        tm = update.message
        update_user(tm.from_user)
        # todo: non-text
        if not tm.text:
            return None
        msg = Message({
            'content': {
                'text': tm.text
                },
            'origin': f'{bot.ident()}:chan:{tm.chat.id}',
            'user': f'telegram:user:{tm.from_user.id}'
            })
        if tm.reply_to_message:
            msg['reply_to'] = Message.query_alias(f'telegram:{bot.bot_id}:message:{tm.reply_to_message.message_id}')
        msg.add_alias(f'telegram:{bot.bot_id}:message:{tm.message_id}')
        msg.persist()
        return msg
    return None

def update_user(u: telegram.User):
    TelegramUser(u.id, {
        'first_name': u.first_name,
        'last_name': u.last_name,
        'username': u.username
        })

