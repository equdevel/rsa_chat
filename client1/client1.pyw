#!/usr/bin/python3

import socket
import _thread
# import rsa
from funcs import dt_now, load_keys, send_encrypted, receive_encrypted, encrypt, decrypt, sign, verify, send, receive
from tkinter import *

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client1'
CLIENTS_COUNT = 3


def receive_message():
    while True:
        try:
            sender_nickname = receive_encrypted(s, privkey)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            s.close()
            history_box.insert(END, f'{dt_now()} DISCONNECTED: {error.strerror}\n')
            break
        else:
            # message = receive_encrypted(s, privkey)
            data = receive(s)
            signature = data[:512]
            message = data[512:]
            # message = b'X' + message[1:]  # modify encrypted message
            if verify(message, signature, client_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                if sender_nickname in (opponent_nickname, 'SERVER'):
                    history_box.insert(END, f'{dt_now()} <{sender_nickname}> {message}\n')


def connect_button_clicked():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError as error:
        history_box.insert(END, f'{dt_now()} NOT CONNECTED: {error.strerror}\n')
    else:
        history_box.insert(END, f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>\n')
        send_encrypted(s, NICKNAME, server_pubkey)
        _thread.start_new_thread(receive_message, ())


def send_button_clicked():
    global opponent_nickname
    data = message_box.get()  # message_box.get('0.0', END)
    data_split = data.split()
    match data_split:
        case['/quit' | '/exit']:
            s.close()
            print(f'{dt_now()} {data}\n{dt_now()} DISCONNECTED')
            # history_box.insert(END, f'{dt_now()} {data}\n{dt_now()} DISCONNECTED\n')
            message_box.delete(0, END)
        case ['/opponent', nickname]:
            opponent_nickname = nickname
            history_box.insert(END, f'{dt_now()} {data}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>\n')
            message_box.delete(0, END)
        case _:
            if data[0] == '@' and len(data_split) == 1:
                opponent_nickname = data_split[0][1:]
                history_box.insert(END, f'{dt_now()} {data}\n{dt_now()} OPPONENT SET TO <{opponent_nickname}>\n')
                message_box.delete(0, END)
            else:
                history_box.insert(END, f'{dt_now()} <{NICKNAME}> {data}\n')
                message_box.delete(0, END)  # message_box.delete('0.0', END)
                send_encrypted(s, opponent_nickname, server_pubkey)
                # send_encrypted(s, data, client_pubkey[opponent_nickname])
                data = encrypt(data, client_pubkey[opponent_nickname])
                data = sign(data, privkey) + data
                send(s, data)


def ctrl_return_pressed(event):
    print(event)
    send_button_clicked()


opponent_nickname = None
# client_pubkey = {}

print(f'{dt_now()} LOADING KEYS...', end='')
privkey, client_pubkey = load_keys(NICKNAME, CLIENTS_COUNT)
server_pubkey = client_pubkey['SERVER']
print('OK')

s = None
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
message_box.bind('<Return>', ctrl_return_pressed)
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
