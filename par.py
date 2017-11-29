import asyncio
import concurrent
import logging

logger = logging.getLogger('par')

thread_pool = concurrent.futures.ThreadPoolExecutor()
event_loop = asyncio.get_event_loop()
event_loop.set_default_executor(thread_pool)

def event_loop_exeception_handler(loop, context):
    if 'exception' in context:
        logger.info(context['exception'])
event_loop.set_exception_handler(event_loop_exeception_handler)

def async_execute(func, *args, **kw):
    return asyncio.wrap_future(thread_pool.submit(func, *args, **kw), loop=event_loop)
