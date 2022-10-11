import rsa
from datetime import datetime


def load_privkey(name):
    with open(f'keys/{name}.key') as f:
        # return rsa.PrivateKey.load_pkcs1(f.read())
        return rsa.PrivateKey.load_pkcs1(f.read().encode('utf8'))


def load_pubkey(name):
    with open(f'keys/{name}.pub') as f:
        # return rsa.PublicKey.load_pkcs1(f.read())
        return rsa.PublicKey.load_pkcs1(f.read().encode('utf8'))


def load_keys(nickname, clients_count):
    privkey = load_privkey(nickname)
    pubkey = {}
    if nickname != 'server':
        pubkey['server'] = load_pubkey('server')
    for i in range(1, clients_count + 1):
        if f'client{i}' == nickname:
            continue
        pubkey[f'client{i}'] = load_pubkey(f'client{i}')
    return privkey, pubkey


def dt_now():
    return '[{:%d.%m.%Y %H:%M:%S}]'.format(datetime.now())


def send_encrypted(sock, data, pubkey):
    sock.send(rsa.encrypt(data.encode('utf8'), pubkey))


def receive_encrypted(sock, privkey):
    return rsa.decrypt(sock.recv(1024), privkey).decode('utf8')
