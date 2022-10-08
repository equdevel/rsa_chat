#!/usr/bin/python3

import socket
import _thread
import rsa
from datetime import datetime
from tkinter import *

host = '127.0.0.1'
port = 9999
my_nickname = 'user_two'
opponent_nickname = 'user_one'

with open('keys/private.key') as f:
    privkey = rsa.PrivateKey.load_pkcs1(f.read())

with open('keys/server_public.key') as f:
    server_pubkey = rsa.PublicKey.load_pkcs1(f.read())

with open('keys/%s_public.key' % opponent_nickname) as f:
    opponent_pubkey = rsa.PublicKey.load_pkcs1(f.read())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_message():
    while True:
        message = rsa.decrypt(s.recv(1024), privkey).decode('utf8')
        history_box.insert(END, '[{:%d.%m.%Y %H:%M:%S}] <{}> {}\n'.format(datetime.now(), opponent_nickname, message))


def connect_button_clicked():
    try:
        s.connect((host, port))
    except ConnectionRefusedError as error:
        # s.close()
        # raise SystemExit(error)
        history_box.insert(END, error.strerror + '\n')
    else:
        history_box.insert(END, 'Connected to %s:%i as %s\n' % (host, port, my_nickname))
        s.send(rsa.encrypt(my_nickname.encode('utf8'), server_pubkey))
        _thread.start_new_thread(receive_message, ())


def send_button_clicked():
    msg = message_box.get()  # message_box.get('0.0', END)
    history_box.insert(END, '[{:%d.%m.%Y %H:%M:%S}] <{}> {}\n'.format(datetime.now(), my_nickname, msg))
    message_box.delete(0, END)  # message_box.delete('0.0', END)
    s.send(rsa.encrypt(opponent_nickname.encode('utf8'), server_pubkey))
    s.send(rsa.encrypt(msg.encode('utf8'), opponent_pubkey))


def ctrl_return_pressed(event):
    print(event)
    send_button_clicked()


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
