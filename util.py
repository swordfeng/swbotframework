import re
import yaml

def assert_on_re(name: str, pattern: str):
    regex = re.compile(pattern)
    def assertion(value: str):
        if regex.match(value) is None:
            raise ValueError(f'Invalid {name}: {value}')
    return assertion

assert_ident = assert_on_re('identifier', r'^[A-Za-z0-9\-_\.:]+$')
assert_name = assert_on_re('name', r'^[A-Za-z0-9\-_\.]+$')

def split_ident(ident: str):
    assert_ident(ident)
    ids = ident.split(':')
    return ids

def join_ident(ids: list):
    for name in ids:
        assert_name(name)
    return ':'.join(ids)

def head_ident(ident: str):
    assert_ident(ident)
    sep = len(ident)
    try:
        sep = ident.index(':')
    except ValueError:
        pass
    return ident[:sep]

def yamldump(obj):
    return yaml.dump(obj, default_flow_style=False)