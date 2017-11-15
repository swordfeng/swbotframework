import logging
import sys
from core import *
from core import _
import secret

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.WARN)
logging.basicConfig(level=logging.DEBUG, handlers=[stdout_handler])

logger = logging.getLogger('main')

pm = query_object('pm')

pm.load('global_hook')
pm.load('simple_manager')
pm.load('telegram')

telegram = _('telegram')

telegram.newbot(secret.TELEGRAM_TOKEN)

event_loop.run_forever()
