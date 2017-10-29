import logging
from core import *
from core import _
import secret

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('main')

pm = query_object('pm')

pm.load('global_hook')
pm.load('simple_manager')
pm.load('telegram')

telegram = _('telegram')

telegram.newbot(secret.TELEGRAM_TOKEN)

event_loop.run_forever()
