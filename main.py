import sys

# Older versions of Python don't respect dictionary insertion order.
is_recent_python = sys.version_info >= (3, 6)
assert is_recent_python, "Please upgrade to Python 3.6 or greater"

import base64
import json
import nacl.encoding
import nacl.signing
import time

def get_author(signing_key):
    key_bytes = bytes(signing_key.verify_key)
    key_base64 = base64.encodebytes(key_bytes).strip().decode()
    return '@' + key_base64 + '.ed25519'


def get_signature(signing_key, unsigned_value):
    unsigned_json = json.dumps(unsigned_value, indent=2)
    signature_bytes = signing_key.sign(bytes(unsigned_json, 'utf8')).signature
    signature_base64 = base64.encodebytes(signature_bytes).strip().decode()
    return signature_base64 + '.sig.ed25519'



signing_key = nacl.signing.SigningKey.generate()

value = {}
value['previous'] = None
value['author'] = get_author(signing_key)
value['sequence'] = 1
value['timestamp'] = round(time.time() * 1000)
value['hash'] = 'sha256'
value['content'] = {}
value['content']['type'] = 'post'
value['content']['text'] = 'hello world'
value['signature'] = get_signature(signing_key, value)

print(json.dumps(value, indent=2))
