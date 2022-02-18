#!/usr/bin/python3

import socket
import _thread
import rsa
# from datetime import datetime

with open('keys/server_private.key') as f:
    server_privkey = rsa.PrivateKey.load_pkcs1(f.read())

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '0.0.0.0'
port = 9999
thread_id = []
clients_online = {}

server_socket.bind((host, port))

server_socket.listen(5)


def forward_message(sender_nickname):
    while True:
        sender_socket = clients_online[sender_nickname]
        try:
            receiver_nickname = rsa.decrypt(sender_socket.recv(1024), server_privkey).decode('utf8')
        except ConnectionResetError as error:
            print(error)
            del clients_online[sender_nickname]
            break
        else:
            if receiver_nickname in clients_online.keys():
                message = sender_socket.recv(1024)
                receiver_socket = clients_online[receiver_nickname]
                receiver_socket.send(message)
                print('Forward encrypted message from %s to %s:' % (sender_nickname, receiver_nickname))
                print(message)
            else:
                print('User %s is offline' % receiver_nickname)
                break

while True:
    client_socket, addr = server_socket.accept()
    client_nickname = rsa.decrypt(client_socket.recv(1024), server_privkey).decode('utf8')
    if client_nickname not in clients_online.keys():
        clients_online[client_nickname] = client_socket
        thread_id.append(_thread.start_new_thread(forward_message, (client_nickname,)))
        print('Accept connection from %s %s' % (str(addr), client_nickname))
    else:
        client_socket.close()
        print('Deny connection from %s %s already connected' % (str(addr), client_nickname))
