import logging
from core import *

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('main')

pm = query_object('pm')

pm.load('telegram')

telegram = query_object('telegram')

telegram.newbot('407147501:AAFoBnIpSuaIJ2O87XmXTkav4miHuxztjgY')

event_loop.run_forever()
