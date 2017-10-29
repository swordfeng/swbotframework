import weakref
from util import *
import logging

logger = logging.getLogger('namespace')

cache = {}
lru_cache = list(map(lambda x: None, range(0, 16)))
def cache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'cache: {ident}')
    if ident in cache and cache[ident]() is not obj:
        logger.error('different object with same identifier!')
        # todo: raise
    cache[ident] = weakref.ref(obj, uncache_object)
    obj_pos = 0
    for i in range(1, len(lru_cache)):
        lru_obj = lru_cache[i]
        if obj is lru_obj:
            obj_pos = i
            break
    for i in range(obj_pos+1, len(lru_cache)):
        lru_cache[i-1] = lru_cache[i]
    lru_cache[len(lru_cache)-1] = obj

def uncache_object(obj):
    if isinstance(obj, weakref.ref):
        obj = obj()
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'uncache: {ident}')
    if ident in cache and cache[ident]() is not obj:
        logger.error('different object with same identifier!')
        # todo: raise
    del(cache[ident])
    for i in range(0, len(lru_cache)):
        lru_obj = lru_cache[i]
        if obj is lru_obj:
            lru_cache[i] = None
            break
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
        obj = ns.query(ids[1:])
        if hasattr(obj, 'cacheable') and obj.cacheable:
            cache_object(obj)
        return obj
    except:
        logger.info('query_object', exc_info=True)
        return None

def _(ident):
    return query_object(ident)

def register_root(obj):
    name = obj.ident()
    assert_name(name)
    logger.info(f'register_root: {name}')
    if name in root_namespace:
        logger.error('duplicated root object!')
        # todo: raise
    root_namespace[name] = obj
    if hasattr(obj, 'on_register_root'):
        obj.on_register_root()

def unregister_root(obj):
    name = obj.ident()
    assert_name(name)
    logger.info(f'unregister_root: {name}')
    if name in root_namespace and root_namespace[name] is not obj:
        logger.error('wrong root object!')
        # todo: raise
    if hasattr(obj, 'on_unregister_root'):
        obj.on_unregister_root()
    del(root_namespace[name])
