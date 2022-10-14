#!/usr/bin/python3

import socket
import _thread
# import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive
from tkinter import *

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client2'
CLIENTS_COUNT = 3


def receive_data():
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
            history_box.insert(END, f'{dt_now()} DISCONNECTED: {error.strerror}\n')
            break
        else:
            sender_nickname = data[0:512]
            sender_nickname = decrypt(sender_nickname, privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            # message = b'X' + message[1:]  # modify encrypted message
            if verify(message, signature, client_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                if sender_nickname in (opponent_nickname, 'SERVER'):
                    history_box.insert(END, f'{dt_now()} <{sender_nickname}> {message}\n')


def connect_button_clicked():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError as error:
        history_box.insert(END, f'{dt_now()} NOT CONNECTED: {error.strerror}\n')
    else:
        history_box.insert(END, f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>\n')
        send_encrypted(sock, NICKNAME, server_pubkey)
        _thread.start_new_thread(receive_data, ())


def send_button_clicked():
    global opponent_nickname
    message = message_box.get()  # message_box.get('0.0', END)
    message_split = message.split()
    match message_split:
        case['/quit' | '/exit']:
            sock.close()
            print(f'{dt_now()} {message}\n{dt_now()} DISCONNECTED')
            # history_box.insert(END, f'{dt_now()} {data}\n{dt_now()} DISCONNECTED\n')
            message_box.delete(0, END)
        case ['/opponent', nickname]:
            opponent_nickname = nickname
            history_box.insert(END, f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>\n')
            message_box.delete(0, END)
        case _:
            if message[0] == '@' and len(message_split) == 1:
                opponent_nickname = message_split[0][1:]
                history_box.insert(END, f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>\n')
                message_box.delete(0, END)
            else:
                history_box.insert(END, f'{dt_now()} <{NICKNAME}> {message}\n')
                message_box.delete(0, END)  # message_box.delete('0.0', END)
                nickname = encrypt(opponent_nickname, server_pubkey)
                message = encrypt(message, client_pubkey[opponent_nickname])
                signature = sign(message, privkey)
                data = nickname + message + signature
                send(sock, data)


def return_pressed(event):
    print(event)
    send_button_clicked()


opponent_nickname = None

privkey, client_pubkey = load_keys(NICKNAME, CLIENTS_COUNT)
server_pubkey = client_pubkey['SERVER']

sock = None

root = Tk()
root.title('RSA_chat 1.0')
root.minsize(800, 600)
root.geometry('800x600+500+200')
root.resizable(width=False, height=False)
frame1 = Frame(root, bd=5)
frame2 = Frame(root, bd=5)
history_box = Text(frame1, width=96, height=33, wrap=WORD)
history_scrollbar = Scrollbar(frame1, command=history_box.yview)
history_box['yscrollcommand'] = history_scrollbar.set
message_box = Entry(frame2, width=98, font='TkFixedFont')  # Text(frame2, width=98, height=2, wrap=WORD)
message_box.bind('<Return>', return_pressed)
connect_button = Button(frame2, text='Connect', width=15, command=connect_button_clicked)
send_button = Button(frame2, text='Send message', width=15, command=send_button_clicked)
frame1.pack()
frame2.pack()
history_box.pack(side=LEFT)
history_scrollbar.pack(side=LEFT, fill=Y)
message_box.pack(side=TOP)
message_box.focus()
connect_button.pack(side=LEFT)
send_button.pack(side=RIGHT)
connect_button_clicked()
root.mainloop()
