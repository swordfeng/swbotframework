import json
import os
import urllib
import urllib.parse
import sqlite3

db_name = 'persistence'
conn = sqlite3.connect(f'{db_name}.db')

with conn:
    conn.execute('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')

def get(key: str):
    with conn:
        for row in conn.execute('SELECT value FROM kv WHERE key = ?', [key]):
            return row[0]
        return None

def put(key: str, value: str):
    with conn:
        if value is not None:
            conn.execute('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', [key, value])
        else:
            conn.execute('DELETE FROM kv WHERE key = ?', [key])

def get_json(key: str):
    v = get(key)
    if v is None:
        return None
    return json.loads(get(key))

def put_json(key: str, value):
    put(key, json.dumps(value))
