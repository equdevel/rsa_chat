#!/usr/bin/python3

import socket
import _thread

# import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive

HOST = '0.0.0.0'
PORT = 9999
CLIENTS_COUNT = 3


def forward_data(sender_nickname):
    sender_socket = clients_online[sender_nickname]
    while True:
        try:
            data = receive(sender_socket)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sender_socket.close()
            del clients_online[sender_nickname]
            print(f'{dt_now()} <{sender_nickname}> DISCONNECTED: {error.strerror}')
            break
        else:
            receiver_nickname = data[0:512]
            receiver_nickname = decrypt(receiver_nickname, server_privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            if verify(message, signature, client_pubkey[sender_nickname]):
                if receiver_nickname in clients_online.keys():
                    receiver_socket = clients_online[receiver_nickname]
                    nickname = encrypt(sender_nickname, client_pubkey[receiver_nickname])
                    data = nickname + message + signature
                    send(receiver_socket, data)
                    print(f'{dt_now()} FORWARD encrypted message from <{sender_nickname}> to <{receiver_nickname}>:')
                    print(data)
                else:
                    nickname = encrypt('SERVER', client_pubkey[sender_nickname])
                    message = f'MESSAGE NOT DELIVERED: <{receiver_nickname}> is offline.'
                    print(f'{dt_now()} {message}')
                    message = encrypt(message, client_pubkey[sender_nickname])
                    signature = sign(message, server_privkey)
                    data = nickname + message + signature
                    send(sender_socket, data)


print(f'{HOST=}\n{PORT=}\n{CLIENTS_COUNT=}')
print(f'{dt_now()} STARTING SERVER...')

thread_id = []
clients_online = {}

server_privkey, client_pubkey = load_keys('SERVER', CLIENTS_COUNT)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f'{dt_now()} SERVING ON {HOST}:{PORT}...')

while True:
    client_socket, client_address = server_socket.accept()
    client_nickname = receive_encrypted(client_socket, server_privkey)
    if client_nickname in client_pubkey.keys():
        if client_nickname not in clients_online.keys():
            clients_online[client_nickname] = client_socket
            thread_id.append(_thread.start_new_thread(forward_data, (client_nickname,)))
            print(f'{dt_now()} <{client_nickname}> CONNECTED from {client_address}')
        else:
            client_socket.close()
            print(f'{dt_now()} ACCESS DENIED from {client_address}: <{client_nickname}> already connected')
            # TODO: send diag message to client
    else:
        client_socket.close()
        print(f'{dt_now()} ACCESS DENIED from {client_address}: <{client_nickname}> not registered')
        # TODO: send diag message to client
