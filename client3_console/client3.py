#!/usr/bin/python3

import socket
import _thread
import rsa
from datetime import datetime

host = '127.0.0.1'
port = 9999
my_nickname = 'user_two'
opponent_nickname = 'user_one'

with open('keys/private.key') as f:
    privkey = rsa.PrivateKey.load_pkcs1(f.read())

with open('keys/server_public.key') as f:
    server_pubkey = rsa.PublicKey.load_pkcs1(f.read())

with open('keys/%s_public.key' % opponent_nickname) as f:
    opponent_pubkey = rsa.PublicKey.load_pkcs1(f.read())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((host, port))
except ConnectionRefusedError as error:
    s.close()
    raise SystemExit(error)
else:
    print('Connected to %s:%i as %s\n' % (host, port, my_nickname))

s.send(rsa.encrypt(my_nickname.encode('utf8'), server_pubkey))


def receive_message():
    while True:
        message = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        print('[{:%d.%m.%Y %H:%M:%S}] <{}> {}'.format(datetime.now(), opponent_nickname, message))

_thread.start_new_thread(receive_message, ())

while True:
    msg = input()
    s.send(rsa.encrypt(opponent_nickname.encode('utf8'), server_pubkey))
    s.send(rsa.encrypt(msg.encode('utf8'), opponent_pubkey))
