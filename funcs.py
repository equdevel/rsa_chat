import pathlib
import rsa
from rsa import VerificationError
from datetime import datetime

BUFSIZE = 1536


def load_privkey(file):
    with open(file) as f:
        return rsa.PrivateKey.load_pkcs1(f.read().encode('utf8'))


def load_pubkey(file):
    with open(file) as f:
        return rsa.PublicKey.load_pkcs1(f.read().encode('utf8'))


def load_keys(nickname):
    print(f'{dt_now()} LOADING KEYS...', end='')
    privkey = load_privkey(f'keys/{nickname}.key')
    pubkey = {}
    for file in pathlib.Path('keys').glob('*.pub'):
        file = file.as_posix()
        nickname = file.removeprefix('keys/').removesuffix('.pub')
        pubkey[nickname] = load_pubkey(file)
    print('OK')
    return privkey, pubkey


def dt_now():
    return '[{:%d.%m.%Y %H:%M:%S}]'.format(datetime.now())


def encrypt(data, pubkey):
    return rsa.encrypt(data.encode('utf8'), pubkey)


def decrypt(data, privkey):
    return rsa.decrypt(data, privkey).decode('utf8')


def sign(data, privkey):
    return rsa.sign(data, privkey, 'SHA-256')


def verify(data, sig, pubkey):
    try:
        res = rsa.verify(data, sig, pubkey) == 'SHA-256'
    except VerificationError:
        res = False
    return res


def send(sock, data):
    sock.send(data)


def receive(sock):
    return sock.recv(BUFSIZE)


def send_encrypted(sock, data, pubkey):
    send(sock, encrypt(data, pubkey))


def receive_encrypted(sock, privkey):
    return decrypt(receive(sock), privkey)
