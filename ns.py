import weakref
from util import *
import logging

logger = logging.getLogger('namespace')

cache = {}

def cache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'cache: {ident}')
    def obj_cleanup(ref):
        logger.info(f'uncache(GC): {ident}')
        obj = ref()
        del(cache[ident])
        if hasattr(obj, 'on_uncache'):
            obj.on_uncache()
    cache[ident] = weakref.ref(obj, obj_cleanup)

def uncache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'uncache: {ident}')
    del(cache[ident])
    if hasattr(obj, 'on_uncache'):
        obj.on_uncache()

root_namespace = {}

def query_object(ident):
    assert_ident(ident)
    logger.info(f'query_object: {ident}')
    try:
        if ident in cache:
            obj = cache[ident]()
            if obj is not None:
                return obj
        ids = split_ident(ident)
        ns = root_namespace[ids[0]]
        if len(ids) == 1:
            return ns
        return ns.query(ids[1:])
    except:
        logger.info('query_object', exc_info=True)
        return None

def register_root(obj):
    name = obj.ident()
    assert_name(name)
    logger.info(f'register_root: {name}')
    root_namespace[name] = obj

def unregister_root(obj):
    name = obj.ident()
    assert_name(name)
    logger.info(f'unregister_root: {name}')
    del(root_namespace[name])
