#!/usr/bin/python3

import socket
import _thread
import rsa
from datetime import datetime

host = '127.0.0.1'
port = 9999
nickname = 'user_three'


def dt_now():
    return '[{:%d.%m.%Y %H:%M:%S}]'.format(datetime.now())


def receive_message():
    while True:
        try:
            opponent_nickname = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        except ConnectionResetError as error:
            s.close()
            print(f'{dt_now()} DISCONNECTED: {error.strerror}')
            break
        else:
            # rsa.sign()
            message = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
            print(f'{dt_now()} <{opponent_nickname}> {message}')


with open('keys/private.key') as f:
    privkey = rsa.PrivateKey.load_pkcs1(f.read())

with open('keys/server_public.key') as f:
    server_pubkey = rsa.PublicKey.load_pkcs1(f.read())

with open('keys/user_one_public.key') as f:
    opponent_pubkey = rsa.PublicKey.load_pkcs1(f.read())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((host, port))
except ConnectionRefusedError as error:
    raise SystemExit(f'{dt_now()} NOT CONNECTED: {error.strerror}')
else:
    print(f'{dt_now()} CONNECTED to {host}:{port} as <{nickname}>')

s.send(rsa.encrypt(nickname.encode('utf8'), server_pubkey))

_thread.start_new_thread(receive_message, ())
while True:
    data = input()
    match data.split():
        case ['/quit']:
            # s.send(rsa.encrypt(data.encode('utf8'), server_pubkey))
            s.close()
            print(f'{dt_now()} DISCONNECTED')
            break
        # case _:
        case ['/send', nickname, message]:
            s.send(rsa.encrypt(nickname.encode('utf8'), server_pubkey))
            s.send(rsa.encrypt(message.encode('utf8'), opponent_pubkey))
