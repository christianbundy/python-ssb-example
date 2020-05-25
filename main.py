import time
import sqlite3
import nacl.signing
import nacl.encoding
import json
import hashlib
import base64
import sys

# Older versions of Python don't respect dictionary insertion order.
is_recent_python = sys.version_info >= (3, 6)
assert is_recent_python, "Please upgrade to Python 3.6 or greater"


conn = sqlite3.connect('ssb.db')

c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS state (
               key text,
               author text,
               sequence number
             )''')
conn.commit()


def get_author_id(verify_key):
    key_bytes = bytes(verify_key)
    key_base64 = base64.encodebytes(key_bytes).strip().decode()
    return '@' + key_base64 + '.ed25519'


def get_signature(signing_key, unsigned_value):
    unsigned_json = json.dumps(unsigned_value, indent=2)
    unsigned_json_bytes = bytes(unsigned_json, 'utf8')
    signature_bytes = signing_key.sign(unsigned_json_bytes).signature
    signature_base64 = base64.encodebytes(signature_bytes).strip().decode()
    return signature_base64 + '.sig.ed25519'


def get_message_id(signed_value):
    signed_json = json.dumps(signed_value, indent=2)
    signed_json_bytes = bytes(signed_json, 'utf8')
    hash_bytes = hashlib.sha256()
    hash_bytes.update(signed_json_bytes)
    hash_digest = hash_bytes.digest()
    hash_base64 = base64.encodebytes(hash_digest).strip().decode()
    return '%' + hash_base64 + '.sha256'


def get_previous(author):
    c.execute('''SELECT key, sequence
                 FROM state
                 WHERE author = ?
                 ORDER BY sequence''', [author])
    result = c.fetchone()
    if result is None:
        return (None, 0)
    else:
        return result


signing_key = nacl.signing.SigningKey.generate()


def create_message(content):
    author = get_author_id(signing_key.verify_key)
    author_state = get_previous(author)  # key, sequence

    value = {}
    value['previous'] = author_state[0]
    value['author'] = author
    value['sequence'] = author_state[1] + 1
    value['timestamp'] = round(time.time() * 1000)
    value['hash'] = 'sha256'
    value['content'] = content
    value['signature'] = get_signature(signing_key, value)

    key = get_message_id(value)

    # Insert a row of data
    c.execute("INSERT INTO state (key, author, sequence) VALUES (?, ?, ?)",
              [key, author, value['sequence']])
    conn.commit()

    return value


hello = create_message({'type': 'post', 'text': 'hello'})
world = create_message({'type': 'post', 'text': 'world'})

print(json.dumps([hello, world]))
