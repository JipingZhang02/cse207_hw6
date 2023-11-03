from sage.all import *
import struct
import re
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5

def b64_enc(s):
    return base64.encodebytes(s).decode("ascii")

def b64_dec(s):
    return base64.b64decode(s)

# Our "MPI" format consists of 4-byte integer length l followed by l bytes of binary key
def int_to_mpi(z):
    s = int_to_binary(z)
    return struct.pack('<I',len(s))+s

# Get bytes representation of arbitrary-length long int
def int_to_binary(z):
    z = int(z)
    return z.to_bytes((z.bit_length() + 7) // 8, 'big')

def bits_to_mpi(s):
    return struct.pack('I',len(s))+s

encrypt_header = '-----BEGIN PRETTY BAD ENCRYPTED MESSAGE-----\n'
encrypt_footer = '-----END PRETTY BAD ENCRYPTED MESSAGE-----\n'

# PKCS 7 pad message.
def pad(s,blocksize=AES.block_size):
    n = blocksize-(len(s)%blocksize)
    return s+bytes([n]*n)

# Encrypt string s using RSA encryption with AES in CBC mode.
# Generate a 256-bit symmetric key, encrypt it using RSA with PKCS1v1.5 padding, and prepend the MPI-encoded RSA ciphertext to the AES-encrypted ciphertext of the message.
def encrypt(rsakey,s):
    aeskey = Random.new().read(32)

    pkcs = PKCS1_v1_5.new(rsakey)
    output = bits_to_mpi(pkcs.encrypt(aeskey))
    
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(aeskey, AES.MODE_CBC, iv)

    output += iv + cipher.encrypt(pad(s))
    return encrypt_header + b64_enc(output) + encrypt_footer

if __name__=='__main__':
    pubkey = RSA.importKey(open('key.pem').read())
    plaintext = open('hw6.pdf', 'rb').read()

    f = open('hw6.pdf.enc.asc','w')
    f.write(encrypt(pubkey,plaintext))
    f.close()
