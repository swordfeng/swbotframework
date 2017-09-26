import json
import os
import urllib

db_name = 'persistence'

if not os.path.exists(db_name):
    os.mkdir(db_name)

def get(key: str):
    fkey = urllib.parse.quote(key, '')
    fname = os.path.join(db_name, fkey)
    if not os.path.exists(fname):
        return None
    with open(fname, 'r') as f:
        return f.read()

def put(key: str, value: str):
    fkey = urllib.parse.quote(key, '')
    fname = os.path.join(db_name, fkey)
    if value is None:
        if os.path.exists(fname):
            os.remove(fname)
        return
    with open(fname, 'w') as f:
        return f.write(value)

def get_json(key: str):
    v = get(key)
    if v is None:
        return None
    return json.loads(get(key))

def put_json(key: str, value):
    put(key, json.dumps(value))
