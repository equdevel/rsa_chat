#!/usr/bin/python3

import socket
import _thread
import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client3'
CLIENTS_COUNT = 3


def receive_data():
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
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


opponent_nickname = None

privkey, client_pubkey = load_keys(NICKNAME, CLIENTS_COUNT)
server_pubkey = client_pubkey['SERVER']

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((HOST, PORT))
except ConnectionRefusedError as error:
    exit(f'{dt_now()} NOT CONNECTED: {error.strerror}')  # raise SystemExit(error_message)
else:
    print(f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>')
    send_encrypted(sock, NICKNAME, server_pubkey)
    _thread.start_new_thread(receive_data, ())

while True:
    message = input()
    message_split = message.split()
    match message_split:
        case ['/quit' | '/exit']:
            sock.close()
            print(f'{dt_now()} DISCONNECTED')
            break
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
