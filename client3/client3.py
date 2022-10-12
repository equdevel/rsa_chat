#!/usr/bin/python3

import socket
import _thread
import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client3'
CLIENTS_COUNT = 3


def receive_message():
    while True:
        try:
            sender_nickname = receive_encrypted(s, privkey)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            s.close()
            print(f'{dt_now()} DISCONNECTED: {error.strerror}')
            break
        else:
            # message = receive_encrypted(s, privkey)
            data = receive(s)
            signature = data[:512]
            message = data[512:]
            if verify(message, signature, client_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                if sender_nickname in (opponent_nickname, 'SERVER'):
                    print(f'{dt_now()} <{sender_nickname}> {message}')


opponent_nickname = None
# client_pubkey = {}

print(f'{dt_now()} LOADING KEYS...', end='')
privkey, client_pubkey = load_keys(NICKNAME, CLIENTS_COUNT)
server_pubkey = client_pubkey['SERVER']
# privkey = load_privkey(NICKNAME)
# server_pubkey = load_pubkey('SERVER')
# for i in range(1, CLIENTS_COUNT+1):
#     if f'client{i}' == NICKNAME:
#         continue
#     client_pubkey[f'client{i}'] = load_pubkey(f'client{i}')
print('OK')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))
except ConnectionRefusedError as error:
    exit(f'{dt_now()} NOT CONNECTED: {error.strerror}')  # raise SystemExit(error_message)
else:
    print(f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>')
    send_encrypted(s, NICKNAME, server_pubkey)
    _thread.start_new_thread(receive_message, ())

while True:
    data = input()
    data_split = data.split()
    match data_split:
        case ['/quit' | '/exit']:
            s.close()
            print(f'{dt_now()} DISCONNECTED')
            break
        # case ['/send' | '/out', nickname, message]:
        case ['/opponent', nickname]:
            opponent_nickname = nickname
            print(f'{dt_now()} OPPONENT SET TO <{opponent_nickname}>')
        case _:
            if data[0] == '@' and len(data_split) == 1:  # data.startswith('@')
                opponent_nickname = data_split[0][1:]
                print(f'{dt_now()} OPPONENT SET TO <{opponent_nickname}>')
            else:
                print(f'{dt_now()} <{NICKNAME}> {data}')
                # TODO: merge signature + receiver_nickname + message into one, and check BUFSIZE
                send_encrypted(s, opponent_nickname, server_pubkey)
                # send_encrypted(s, data, client_pubkey[opponent_nickname])
                data = encrypt(data, client_pubkey[opponent_nickname])
                data = sign(data, privkey) + data
                send(s, data)
