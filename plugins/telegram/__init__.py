from core import *
import db
import logging
import telegram
import asyncio

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
            logger.info('poll')
            updates = await async_execute(self.bot.getUpdates, offset=self.last_update)
            logger.info('updates')
            for update in updates:
                if update.update_id >= self.last_update:
                    self.last_update = update.update_id + 1
                msg = telegram2message(update, self)
                if msg is not None:
                    chan = query_object(msg['origin'])
                    chan.on_receive(msg)

class TelegramChannel(Channel):
    def __init__(self, chat: telegram.Chat, bot: TelegramBot):
        self.bot = bot
        self.chat = chat
        self.chat_id = chat.id
        super().__init__() # load config, cache
    def ident(self):
        return f'{self.bot.ident()}:chan:{self.chat_id}'
    def send_message(self, msg: Message, chan: Channel):
        if 'file' in msg:
            pass # senddocuemnt
        elif 'image' in msg:
            pass # sendphoto
        elif 'text' in msg:
            pass # sendmessage
        else:
            logger.warning(f'ignored message: {msg}')
    def on_update(self, msg: telegram.Message):
        pass

class TelegramUser(User):
    def __init__(self):
        cache_object(self)
    def ident(self):
        pass
    def persist(self):
        pass
    def on_uncache(self):
        self.persist()
    def display_name(self):
        pass

def telegram2message(update: telegram.Update, bot: TelegramBot):
    if update.message:
        tm = update.message
        msg = Message({
            'text': tm.text,
            'origin': f'{bot.ident()}:chan:{tm.chat.id}',
            'user': f'telegram:user:{tm.from_user.id}'
            })
        if tm.reply_to_message:
            msg['reply_to'] = Message.query_alias(f'telegram:message:{bot.bot_id}:{tm.message_id}')
        msg.add_alias('tele
        return msg
    return None
