import logging
from core import *
from secret import *

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('main')

pm = query_object('pm')

pm.load('global_hook')
pm.load('echo')
pm.load('telegram')

telegram = query_object('telegram')

telegram.newbot(TELEGRAM_TOKEN)

event_loop.run_forever()
