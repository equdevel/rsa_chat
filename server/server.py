#!/usr/bin/python3

import socket
import _thread
import rsa
from datetime import datetime

client_pubkey = {}

with open('keys/server_private.key') as f:
    server_privkey = rsa.PrivateKey.load_pkcs1(f.read())

with open('keys/user_one_public.key') as f:
    client_pubkey['user_one'] = rsa.PublicKey.load_pkcs1(f.read())

with open('keys/user_two_public.key') as f:
    client_pubkey['user_two'] = rsa.PublicKey.load_pkcs1(f.read())

with open('keys/user_three_public.key') as f:
    client_pubkey['user_three'] = rsa.PublicKey.load_pkcs1(f.read())


host = '0.0.0.0'
port = 9999
thread_id = []
clients_online = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
print(f'Serving on {host}:{port}...')


def dt_now():
    return '[{:%d.%m.%Y %H:%M:%S}]'.format(datetime.now())


def forward_message(sender_nickname):
    while True:
        sender_socket = clients_online[sender_nickname]
        try:
            receiver_nickname = rsa.decrypt(sender_socket.recv(1024), server_privkey).decode('utf8')
        except ConnectionResetError as error:
            sender_socket.close()
            del clients_online[sender_nickname]
            print(f'{dt_now()} <{sender_nickname}> DISCONNECTED: {error.strerror}')
            break
        else:
            if receiver_nickname in clients_online.keys():
                message = sender_socket.recv(1024)
                receiver_socket = clients_online[receiver_nickname]
                receiver_socket.send(rsa.encrypt(sender_nickname.encode('utf8'), client_pubkey[receiver_nickname]))
                receiver_socket.send(message)
                print(f'{dt_now()} FORWARD encrypted message from <{sender_nickname}> to <{receiver_nickname}>:')
                print(message)
            else:
                msg = f'MESSAGE NOT DELIVERED: <{receiver_nickname}> is offline.'
                print(f'{dt_now()} {msg}')
                sender_socket.send(rsa.encrypt('SERVER'.encode('utf8'), client_pubkey[sender_nickname]))
                sender_socket.send(rsa.encrypt(msg.encode('utf8'), client_pubkey[sender_nickname]))
                break


while True:
    client_socket, client_address = server_socket.accept()
    client_nickname = rsa.decrypt(client_socket.recv(1024), server_privkey).decode('utf8')
    if client_nickname not in clients_online.keys():
        clients_online[client_nickname] = client_socket
        thread_id.append(_thread.start_new_thread(forward_message, (client_nickname,)))
        print(f'{dt_now()} <{client_nickname}> CONNECTED from {client_address}')
    else:
        client_socket.close()
        print(f'{dt_now()} ACCESS DENIED from {client_address}: <{client_nickname}> already connected')
