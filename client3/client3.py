#!/usr/bin/python3

import socket
import _thread
import rsa
from funcs import dt_now, load_privkey, load_pubkey, load_keys

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client3'
CLIENTS_COUNT = 3


def receive_message():
    while True:
        try:
            sender_nickname = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        except ConnectionResetError as error:
            s.close()
            print(f'{dt_now()} DISCONNECTED: {error.strerror}')
            break
        else:
            # rsa.verify(message, signature, pubkey)
            message = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
            if sender_nickname == opponent_nickname:
                print(f'{dt_now()} <{opponent_nickname}> {message}')


opponent_nickname = None
client_pubkey = {}

print(f'{dt_now()} LOADING KEYS...', end='')
privkey, client_pubkey = load_keys(NICKNAME, CLIENTS_COUNT)
server_pubkey = client_pubkey['server']
# privkey = load_privkey(NICKNAME)
# server_pubkey = load_pubkey('server')
# for i in range(1, CLIENTS_COUNT+1):
#     if f'client{i}' == NICKNAME:
#         continue
#     client_pubkey[f'client{i}'] = load_pubkey(f'client{i}')
print('OK')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))
except ConnectionRefusedError as error:
    raise SystemExit(f'{dt_now()} NOT CONNECTED: {error.strerror}')
else:
    print(f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>')

s.send(rsa.encrypt(NICKNAME.encode('utf8'), server_pubkey))

_thread.start_new_thread(receive_message, ())
while True:
    data = input()
    match data.split():
        case ['/quit' | '/exit']:
            s.close()
            print(f'{dt_now()} DISCONNECTED')
            break
        # case ['/send', nickname, message]:
        case ['/opponent' | '@', nickname]:
            opponent_nickname = nickname
            print(f'{dt_now()} OPPONENT SET TO <{opponent_nickname}>')
        case _:
            s.send(rsa.encrypt(opponent_nickname.encode('utf8'), server_pubkey))
            s.send(rsa.encrypt(data.encode('utf8'), client_pubkey[opponent_nickname]))
