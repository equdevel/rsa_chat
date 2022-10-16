#!/usr/bin/python3

import socket
import _thread
import os
import sys
from funcs import dt_now, load_keys, send_encrypted, encrypt, decrypt, sign, verify, send, receive
from tkinter import *

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = os.path.basename(sys.argv[0]).split(sep='.', maxsplit=1)[0]
OPPONENT_NICKNAME = 'client1'


def receive_data():
    global connected
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
            connected = False
            history_box.insert(END, f'{dt_now()} DISCONNECTED: {error.strerror}\n')
            break
        else:
            sender_nickname = data[0:512]
            sender_nickname = decrypt(sender_nickname, privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            if verify(message, signature, client_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                if sender_nickname in (OPPONENT_NICKNAME, 'SERVER'):
                    history_box.insert(END, f'{dt_now()} <{sender_nickname}> {message}\n')


def connect_button_clicked():
    global sock, connected
    if not connected:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        history_box.insert(END, f'{dt_now()} /connect\n{dt_now()} CONNECTING to {HOST}:{PORT} as <{NICKNAME}>...\n')
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError as error:
            history_box.insert(END, f'{dt_now()} NOT CONNECTED: {error.strerror}\n')
        else:
            send_encrypted(sock, NICKNAME, server_pubkey)
            message = receive(sock).decode('utf8')
            history_box.insert(END, f'{dt_now()} {message}\n')
            if message == 'CONNECTED':
                _thread.start_new_thread(receive_data, ())
                connected = True
            else:
                sock.close()
                connected = False


def disconnect_button_clicked():
    global connected
    if connected:
        sock.close()
        connected = False
        history_box.insert(END, f'{dt_now()} /exit\n')
        print(f'{dt_now()} /exit\n{dt_now()} DISCONNECTED')
        message_box.delete(0, END)


def send_button_clicked():
    global OPPONENT_NICKNAME, connected
    # TODO: send message with all \n, use Ctrl+Enter for send_button_clicked()
    message = message_box.get('0.0', END)[:-1][:300]  # delete \n at end and limit to 300 symbols
    if connected and len(message) > 0:
        message_split = message.split(maxsplit=1)
        match message_split:
            case ['/connect']:
                connect_button_clicked()
            case ['/quit' | '/exit']:
                disconnect_button_clicked()
            case ['/opponent', nickname]:
                OPPONENT_NICKNAME = nickname
                history_box.insert(END, f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
                message_box.delete(0, END)
            case _:
                if message[0] == '@' and len(message_split) == 1:
                    OPPONENT_NICKNAME = message[1:]
                    history_box.insert(END, f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
                    message_box.delete(0, END)
                else:
                    history_box.insert(END, f'{dt_now()} <{NICKNAME}> {message}\n')
                    message_box.delete('0.0', END)
                    nickname = encrypt(OPPONENT_NICKNAME, server_pubkey)
                    message = encrypt(message, client_pubkey[OPPONENT_NICKNAME])
                    signature = sign(message, privkey)
                    data = nickname + message + signature
                    send(sock, data)


def return_pressed(event):
    print(event)
    send_button_clicked()


sock = None
connected = False

root = Tk()
root.title('RSA_chat 2.0')
root.minsize(800, 600)
root.geometry('800x600+500+200')
root.resizable(width=False, height=False)

contacts_listbox = Listbox(root, selectmode=SINGLE)
contacts_scrollbar = Scrollbar(root, command=contacts_listbox.yview)
contacts_listbox['yscrollcommand'] = contacts_scrollbar.set
contacts_listbox.insert(1, OPPONENT_NICKNAME)

history_box = Text(root, wrap=WORD)
history_scrollbar = Scrollbar(root, command=history_box.yview)
history_box['yscrollcommand'] = history_scrollbar.set

# message_box = Entry(root, width=98, font='TkFixedFont')
message_box = Text(root, wrap=WORD)
message_box.bind('<Return>', return_pressed)

connect_button = Button(root, text='Connect', command=connect_button_clicked)
disconnect_button = Button(root, text='Disconnect', command=disconnect_button_clicked)
send_button = Button(root, text='Send message', command=send_button_clicked)

contacts_listbox.place(relwidth=0.1, relheight=0.8)
contacts_scrollbar.place(relwidth=0.02, relheight=0.8, relx=0.1)
history_box.place(relwidth=0.86, relheight=0.8, relx=0.12)
history_scrollbar.place(relwidth=0.02, relheight=0.8, anchor=NE, relx=1.0)
message_box.place(relwidth=1.0, relheight=0.12, rely=0.8)
connect_button.place(relwidth=0.2, relheight=0.08, anchor=SW, relx=0.0, rely=1.0)
disconnect_button.place(relwidth=0.2, relheight=0.08, anchor=SW, relx=0.2, rely=1.0)
send_button.place(relwidth=0.2, relheight=0.08, anchor=SE, relx=1.0, rely=1.0)

history_box.insert(END, f'{HOST=}\n{PORT=}\n{NICKNAME=}\n{OPPONENT_NICKNAME=}\n\n{dt_now()} STARTING CLIENT...\n')
history_box.insert(END, f'{dt_now()} LOADING KEYS...')
privkey, client_pubkey = load_keys(NICKNAME)
server_pubkey = client_pubkey['SERVER']
history_box.insert(END, f'OK\n')

connect_button_clicked()
message_box.focus()
root.mainloop()
