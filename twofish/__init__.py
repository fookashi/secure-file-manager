from ctypes import *
import os
from tempfile import NamedTemporaryFile


so_file = os.getcwd() + "/twofish/twofish.so"

lib = CDLL(so_file)


class twofish_key(Structure):
    _fields_ = [('s', c_uint32*4*256),
                ('K', c_uint32*40)]
    
TwofishSessionKey = POINTER(twofish_key)

class twofish_context(Structure):
    _fields_ = [('iv', c_char_p),
                ('mode', c_int),
                ('key', TwofishSessionKey)]

TwofishContext = POINTER(twofish_context)

CallbackFunc = CFUNCTYPE(None, c_float)

lib.generate_key.restype = TwofishSessionKey
lib.generate_key.argtypes = [c_char_p, c_int]

lib.generate_context.restype = TwofishContext
lib.generate_context.argtypes = [c_char_p, c_int, TwofishSessionKey]

lib.encrypt_block.restype = c_char_p
lib.encrypt_block.argtypes = [TwofishSessionKey, c_char_p]

lib.decrypt_block.restype = c_char_p
lib.decrypt_block.argtypes = [TwofishSessionKey, c_char_p]

lib.encrypt_file.restype = None
lib.encrypt_file.argtypes = [c_char_p, TwofishContext, c_char_p, CallbackFunc]

lib.decrypt_file.restype = None
lib.decrypt_file.argtypes = [c_char_p, TwofishContext, c_char_p, CallbackFunc]


def generate_key(data: bytes, key_size: int) -> TwofishSessionKey:
    return lib.generate_key(c_char_p(data), c_int(key_size))

def generate_context(iv: bytes, mode: int, key: TwofishSessionKey) -> TwofishContext:
    return lib.generate_context(c_char_p(iv), c_int(mode), key)

def encrypt_file(filepath: str, context: TwofishContext, progress_val):
    tmp = NamedTemporaryFile("wb+")
    def update_progress(progress):
        progress_val.value = progress
    lib.encrypt_file(c_char_p(filepath.encode()), context, tmp.name.encode(), CallbackFunc(update_progress))
    return tmp

def decrypt_file(filepath: str, context: TwofishContext, outpath: str, progress_val):
    def update_progress(progress):
        progress_val.value = progress
    lib.decrypt_file(c_char_p(filepath.encode()), context, c_char_p(outpath.encode()), CallbackFunc(update_progress))