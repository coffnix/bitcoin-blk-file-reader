#!/usr/bin/env python3

"""encode/decode base58 in the same way that Bitcoin does"""

import math
import hashlib

__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
    """ encode v, which is a string of bytes, to base58.		
    """
    # v deve ser bytes em Py3
    long_value = int.from_bytes(v, 'big')

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == 0: nPad += 1
        else: break

    return (__b58chars[0] * nPad) + result

def b58decode(v, length):
    """ decode v into a string of len bytes
    """
    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base ** i)
    
    result = b''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = bytes([mod]) + result
        long_value = div
    result = bytes([long_value]) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]: nPad += 1
        else: break

    result = b'\x00' * nPad + result
    if length is not None and len(result) != length:
        return None

    return result

def sha_256(data):
    return hashlib.sha256(data).digest()

def checksum(data):
    return sha_256(sha_256(data))

def ripemd_160(data):
    return hashlib.new("ripemd160", data).digest()

def hash_160(public_key):
    h1 = sha_256(public_key)
    h2 = ripemd_160(h1)
    return h2

def public_key_to_bc_address(public_key):
    h160 = hash_160(public_key)
    return hash_160_to_bc_address(h160)

def hash_160_to_bc_address(h160):
    vh160 = b"\x00" + h160  # \x00 is version 0
    h3 = sha_256(sha_256(vh160))
    addr = vh160 + h3[0:4]
    return b58encode(addr)

def bc_address_to_hash_160(addr):
    bytes_data = b58decode(addr, 25)
    return bytes_data[1:21]

if __name__ == '__main__':
    x = bytes.fromhex('005cc87f4a3fdfe3a2346b6953267ca867282630d3f9b78e64')
    encoded = b58encode(x)
    print(encoded, '19TbMSWwHvnxAKy12iNm3KdbGfzfaMFViT')
    print(b58decode(encoded, len(x)).hex(), x.hex())
