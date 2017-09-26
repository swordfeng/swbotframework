import weakref
from util import *

cache = {}

def cache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    def obj_cleanup(ref):
        obj = ref()
        del(cache[ident])
        if hasattr(obj, 'on_uncache'):
            obj.on_uncache()
    cache[ident] = weakref.ref(obj, obj_cleanup)

def uncache_object(obj):
    ident = obj.ident()
    assert_ident(ident)
    del(cache[ident])
    if hasattr(obj, 'on_uncache'):
        obj.on_uncache()

root_namespace = {}

def query_object(ident):
    assert_ident(ident)
    if ident in cache:
        obj = cache[ident]()
        if obj is not None:
            return obj
    ids = split_ident(ident)
    ns = root_namespace[ids[0]] # throws
    if len(ids) == 1:
        return ns
    return ns.query(ids[1:])

def register_root(obj):
    name = obj.ident()
    assert_name(name)
    root_namespace[name] = obj

def unregister_root(obj):
    name = obj.ident()
    assert_name(name)
    del(root_namespace[name])
