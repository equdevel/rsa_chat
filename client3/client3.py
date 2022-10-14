#!/usr/bin/python3

import socket
import _thread
import os
import sys
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = os.path.basename(sys.argv[0]).split(sep='.', maxsplit=1)[0]


def receive_data():
    global connected
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
            connected = False
            print(f'{dt_now()} DISCONNECTED: {error.strerror}')
            break
        else:
            sender_nickname = data[0:512]
            sender_nickname = decrypt(sender_nickname, privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            if verify(message, signature, client_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                if sender_nickname in (opponent_nickname, 'SERVER'):
                    print(f'{dt_now()} <{sender_nickname}> {message}')


print(f'{HOST=}\n{PORT=}\n{NICKNAME=}')
print(f'{dt_now()} STARTING CLIENT...')

opponent_nickname = NICKNAME

privkey, client_pubkey = load_keys(NICKNAME)
server_pubkey = client_pubkey['SERVER']

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connected = False

print(f'{dt_now()} CONNECTING to {HOST}:{PORT} as <{NICKNAME}>...')
try:
    sock.connect((HOST, PORT))
except ConnectionRefusedError as error:
    exit(f'{dt_now()} NOT CONNECTED: {error.strerror}')  # raise SystemExit(error_message)
else:
    send_encrypted(sock, NICKNAME, server_pubkey)
    message = receive(sock).decode('utf8')
    print(f'{dt_now()} {message}')
    if message == 'CONNECTED':
        _thread.start_new_thread(receive_data, ())
        connected = True
    else:
        sock.close()
        exit()

while True:
    message = input()[:300]
    if connected and len(message) > 0:
        message_split = message.split(maxsplit=1)
        match message_split:
            case ['/quit' | '/exit']:
                sock.close()
                exit(f'{dt_now()} DISCONNECTED')
                # break
            # case ['/send' | '/out', nickname, message]:
            case ['/opponent', nickname]:
                opponent_nickname = nickname
                print(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>')
            case _:
                if message[0] == '@' and len(message_split) == 1:  # message.startswith('@') or use regex_spm
                    opponent_nickname = message_split[0][1:]
                    print(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>')
                else:
                    print(f'{dt_now()} <{NICKNAME}> {message}')
                    nickname = encrypt(opponent_nickname, server_pubkey)
                    message = encrypt(message, client_pubkey[opponent_nickname])
                    signature = sign(message, privkey)
                    data = nickname + message + signature
                    send(sock, data)
