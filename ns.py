import weakref
from util import *
import logging

logger = logging.getLogger('namespace')

root_namespace = {}
cache = {}
cache_names = {}
lru_cache = list(map(lambda x: None, range(0, 8)))

def cache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'cache: {ident}')
    if ident in cache and cache[ident]() is not obj:
        logger.error('different object with same identifier!')
        # todo: raise
    # add to cache
    cache[ident] = weakref.ref(obj, uncache_object)
    # add to lru
    obj_pos = 0
    for i in range(1, len(lru_cache)):
        lru_obj = lru_cache[i]
        if obj is lru_obj:
            obj_pos = i
            break
        elif obj is None:
            obj_pos = i
    for i in range(obj_pos, len(lru_cache)-1):
        lru_cache[i] = lru_cache[i+1]
    lru_cache[len(lru_cache)-1] = obj
    # add to names
    name = head_ident(ident)
    if name not in cache_names:
        cache_names[name] = set()
    cache_names[name].add(ident)

def uncache_object(obj):
    byGC = False
    if isinstance(obj, weakref.ref):
        obj = obj()
        byGC = True
    ident = obj.ident()
    assert_ident(ident)
    logger.info(f'uncache{"(GC)" if byGC else ""}: {ident}')
    if ident in cache and cache[ident]() is not obj:
        logger.error('different object with same identifier!')
        # todo: raise
    if hasattr(obj, 'on_uncache'):
        obj.on_uncache()
    # remove from cache
    del(cache[ident])
    # remove from lru
    for i in range(0, len(lru_cache)):
        lru_obj = lru_cache[i]
        if obj is lru_obj:
            lru_cache[i] = None
            break
    # remove from names
    name = head_ident(ident)
    cache_names[name].discard(ident)

def cacheable(klass):
    original_init = klass.__init__
    def init(self, *args, **kw):
        original_init(self, *args, **kw)
        cache_object(self)
    klass.__init__ = init
    return klass

def query_object(ident, suppress_error=True):
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
        return obj
    except:
        logger.info('query_object', exc_info=True)
        if suppress_error:
            return None
        else:
            raise

def _(ident):
    obj = query_object(ident, suppress_error=False)
    if obj is None:
        raise ValueError('Object not found')
    return obj

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
    # remove names
    if name in cache_names:
        for ident in list(cache_names[name]):
            obj = cache[ident]()
            if obj is not None:
                uncache_object(obj)
    del(cache_names[name])
