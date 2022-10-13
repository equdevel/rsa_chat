#!/usr/bin/python3

import socket
import _thread
# import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive

HOST = '0.0.0.0'
PORT = 9999
CLIENTS_COUNT = 3


def forward_message(sender_nickname):
    while True:
        sender_socket = clients_online[sender_nickname]
        try:
            receiver_nickname = receive_encrypted(sender_socket, server_privkey)
        except ConnectionResetError as error:
            sender_socket.close()
            del clients_online[sender_nickname]
            print(f'{dt_now()} <{sender_nickname}> DISCONNECTED: {error.strerror}')
            break
        else:
            message = sender_socket.recv(1024)
            # TODO: verify signature of message with sender_pubkey -> rsa.verify(message, signature, sender_pubkey)
            if receiver_nickname in clients_online.keys():
                receiver_socket = clients_online[receiver_nickname]
                send_encrypted(receiver_socket, sender_nickname, client_pubkey[receiver_nickname])
                receiver_socket.send(message)
                print(f'{dt_now()} FORWARD encrypted message from <{sender_nickname}> to <{receiver_nickname}>:')
                print(message)
            else:
                msg = f'MESSAGE NOT DELIVERED: <{receiver_nickname}> is offline.'
                print(f'{dt_now()} {msg}')
                send_encrypted(sender_socket, 'SERVER', client_pubkey[sender_nickname])
                # send_encrypted(sender_socket, msg, client_pubkey[sender_nickname])
                data = encrypt(msg, client_pubkey[sender_nickname])
                data = sign(data, server_privkey) + data
                send(sender_socket, data)


thread_id = []
clients_online = {}
client_pubkey = {}

print(f'{dt_now()} LOADING KEYS...', end='')
server_privkey, client_pubkey = load_keys('server', CLIENTS_COUNT)
# server_privkey = load_privkey('server')
# for i in range(1, CLIENTS_COUNT+1):
#     client_pubkey[f'client{i}'] = load_pubkey(f'client{i}')
print('OK')

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'{dt_now()} SERVING ON {HOST}:{PORT}...')

while True:
    client_socket, client_address = server_socket.accept()
    client_nickname = receive_encrypted(client_socket, server_privkey)
    # TODO: USER EXISTS? -> if client_nickname in client_pubkey.keys():
    if client_nickname not in clients_online.keys():
        clients_online[client_nickname] = client_socket
        thread_id.append(_thread.start_new_thread(forward_message, (client_nickname,)))
        print(f'{dt_now()} <{client_nickname}> CONNECTED from {client_address}')
    else:
        client_socket.close()
        print(f'{dt_now()} ACCESS DENIED from {client_address}: <{client_nickname}> already connected')
