import asyncio
import concurrent

thread_pool = concurrent.futures.ThreadPoolExecutor()
event_loop = asyncio.get_event_loop()

def async_execute(func, *args, **kw):
    return asyncio.wrap_future(thread_pool.submit(func, *args, **kw), loop=event_loop)
