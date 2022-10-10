#!/usr/bin/python3

import socket
import _thread
import rsa
from funcs import dt_now, load_privkey, load_pubkey
from tkinter import *

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = 'client2'
CLIENTS_COUNT = 3


def receive_message():
    while True:
        opponent_nickname = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        message = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        history_box.insert(END, f'{dt_now()} <{opponent_nickname}> {message}\n')


def connect_button_clicked():
    try:
        s.connect((HOST, PORT))
    except ConnectionRefusedError as error:
        history_box.insert(END, error.strerror + '\n')
    else:
        history_box.insert(END, f'{dt_now()} CONNECTED to {HOST}:{PORT} as <{NICKNAME}>\n')
        s.send(rsa.encrypt(NICKNAME.encode('utf8'), server_pubkey))
        _thread.start_new_thread(receive_message, ())


def send_button_clicked():
    msg = message_box.get()  # message_box.get('0.0', END)
    history_box.insert(END, f'[{dt_now()}] <{NICKNAME}> {msg}\n')
    message_box.delete(0, END)  # message_box.delete('0.0', END)
    s.send(rsa.encrypt('client3'.encode('utf8'), server_pubkey))
    s.send(rsa.encrypt(msg.encode('utf8'), client_pubkey['client3']))


def ctrl_return_pressed(event):
    print(event)
    send_button_clicked()


client_pubkey = {}

print(f'{dt_now()} LOADING KEYS...', end='')
privkey = load_privkey(NICKNAME)
server_pubkey = load_pubkey('server')
for i in range(1, CLIENTS_COUNT+1):
    if f'client{i}' == NICKNAME:
        continue
    client_pubkey[f'client{i}'] = load_pubkey(f'client{i}')
print('OK')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
root.mainloop()
