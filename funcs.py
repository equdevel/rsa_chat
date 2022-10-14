import rsa
from rsa import VerificationError
from datetime import datetime

BUFSIZE = 1536


def load_privkey(name):
    with open(f'keys/{name}.key') as f:
        return rsa.PrivateKey.load_pkcs1(f.read().encode('utf8'))


def load_pubkey(name):
    with open(f'keys/{name}.pub') as f:
        return rsa.PublicKey.load_pkcs1(f.read().encode('utf8'))


def load_keys(nickname, clients_count):
    print(f'{dt_now()} LOADING KEYS...', end='')
    privkey = load_privkey(nickname)
    pubkey = {}
    if nickname != 'SERVER':
        pubkey['SERVER'] = load_pubkey('SERVER')
    for i in range(1, clients_count + 1):
        if f'client{i}' == nickname:
            continue
        pubkey[f'client{i}'] = load_pubkey(f'client{i}')
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
