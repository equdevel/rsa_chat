import rsa
from datetime import datetime


def load_privkey(name):
    with open(f'keys/{name}.key') as f:
        return rsa.PrivateKey.load_pkcs1(f.read())


def load_pubkey(name):
    with open(f'keys/{name}.pub') as f:
        return rsa.PublicKey.load_pkcs1(f.read())


def load_keys(nickname, clients_count, mode):
    privkey = load_privkey(nickname)
    client_pubkey = {}
    for i in range(1, clients_count + 1):
        if f'client{i}' == nickname:
            continue
        client_pubkey[f'client{i}'] = load_pubkey(f'client{i}')
    match mode:
        case 'client':
            server_pubkey = load_pubkey('server')
            return privkey, server_pubkey, client_pubkey
        case 'server':
            return privkey, client_pubkey
        case _:
            return None


def dt_now():
    return '[{:%d.%m.%Y %H:%M:%S}]'.format(datetime.now())
