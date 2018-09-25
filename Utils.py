import sys
import binascii

def binascii_hexlify_py3(n):     
    if sys.version_info >= (3,0):
        if type(n) is bytes:
            return binascii.hexlify(bytes(n))
        elif type(n) is int:
            return binascii.hexlify(bytes([n]))
    else:
        return binascii.hexlify(n)
