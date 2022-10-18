#!/usr/bin/python3

import socket
import _thread
import os
import sys
from funcs import dt_now, load_keys, send_encrypted, encrypt, decrypt, sign, verify, send, receive
from tkinter import *
from tkinter import messagebox

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = os.path.basename(sys.argv[0]).split(sep='.', maxsplit=1)[0]
SERVER = 'SERVER'
DIAG = 'DIAG'


def receive_data():
    global connected
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
            connected = False
            history_append(f'{dt_now()} DISCONNECTED: {error.strerror}\n', DIAG)
            break
        else:
            sender_nickname = data[0:512]
            sender_nickname = decrypt(sender_nickname, privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            if verify(message, signature, contact_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                # if sender_nickname in (OPPONENT_NICKNAME, SERVER):
                history_append(f'{dt_now()} <{sender_nickname}> {message}\n', sender_nickname)


def connect_button_clicked():
    global sock, connected
    if not connected:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        history_append(f'{dt_now()} /connect\n{dt_now()} CONNECTING to {HOST}:{PORT} as <{NICKNAME}>...\n', DIAG)
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError as error:
            history_append(f'{dt_now()} NOT CONNECTED: {error.strerror}\n', DIAG)
        else:
            send_encrypted(sock, NICKNAME, server_pubkey)
            message = receive(sock).decode('utf8')
            history_append(f'{dt_now()} {message}\n', DIAG)
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
        history_append(f'{dt_now()} /exit\n', DIAG)
        message_box.delete('0.0', END)


def send_button_clicked():
    global OPPONENT_NICKNAME, connected
    # TODO: send message with all \n, use Ctrl+Enter for send_button_clicked()
    message = message_box.get('0.0', END)[:-1][:300]  # delete \n at the end and limit to 300 symbols
    if connected and len(message) > 0:
        message_split = message.split(maxsplit=1)
        match message_split:
            case ['/connect']:
                connect_button_clicked()
            case ['/quit' | '/exit']:
                disconnect_button_clicked()
            case ['/opponent', nickname]:
                OPPONENT_NICKNAME = nickname
                history_append(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
                message_box.delete(0, END)
            case _:
                if message[0] == '@' and len(message_split) == 1:
                    OPPONENT_NICKNAME = message[1:]
                    history_append(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
                    message_box.delete(0, END)
                else:
                    history_append(f'{dt_now()} <{NICKNAME}> {message}\n')
                    message_box.delete('0.0', END)
                    nickname = encrypt(OPPONENT_NICKNAME, server_pubkey)
                    message = encrypt(message, contact_pubkey[OPPONENT_NICKNAME])
                    signature = sign(message, privkey)
                    data = nickname + message + signature
                    send(sock, data)


def ctrl_return_pressed(event):
    print(event)
    send_button_clicked()


def history_box_refresh(nickname):
    history_box.delete('0.0', END)
    history_box.insert(END, contact_history[nickname])


def contact_select(event):
    global OPPONENT_NICKNAME
    print(event)
    # print(contacts_listbox.curselection())
    OPPONENT_NICKNAME = contacts_listbox.selection_get()
    history_box_refresh(OPPONENT_NICKNAME)


def history_append(s, *args):
    if len(args) == 1:
        nickname = args[0]
        contact_history[nickname] += s
        if nickname == OPPONENT_NICKNAME:
            history_box_refresh(nickname)
    else:
        nickname = OPPONENT_NICKNAME
        contact_history[nickname] += s
        history_box_refresh(nickname)
    with open(f'history/{nickname}.txt', mode='a') as f:
        f.write(s)


def on_closing():
    # if messagebox.askokcancel("Quit", "Do you want to quit?"):
    sock.close()
    root.destroy()


sock = None
connected = False
contact_history = {}

root = Tk()
root.title(f'RSA-chat <{NICKNAME}>')
root.minsize(800, 600)
root.geometry('800x600+500+200')
root.resizable(width=False, height=False)

contacts_listbox = Listbox(root, selectmode=SINGLE)
contacts_scrollbar = Scrollbar(root, command=contacts_listbox.yview)
contacts_listbox['yscrollcommand'] = contacts_scrollbar.set
contacts_listbox.bind('<<ListboxSelect>>', contact_select)

history_box = Text(root, wrap=WORD)
history_scrollbar = Scrollbar(root, command=history_box.yview)
history_box['yscrollcommand'] = history_scrollbar.set

# message_box = Entry(root, font='TkFixedFont')
message_box = Text(root, wrap=WORD)
# message_box.configure()
message_box.bind('<Control-Return>', ctrl_return_pressed)

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

privkey, contact_pubkey = load_keys(NICKNAME)
server_pubkey = contact_pubkey[SERVER]

# for i, nickname in enumerate(contact_pubkey.keys()):
for nickname in (DIAG, *contact_pubkey.keys()):
    try:
        with open(f'history/{nickname}.txt', mode='r') as f:
            contact_history[nickname] = f.read()
    except FileNotFoundError:
        contact_history[nickname] = ''
    contacts_listbox.insert(END, nickname)

contacts_listbox.selection_set(0)
OPPONENT_NICKNAME = DIAG
# OPPONENT_NICKNAME = contacts_listbox.selection_get()

history_append(f'{HOST=}\n{PORT=}\n{NICKNAME=}\n\n{dt_now()} STARTING CLIENT...\n', DIAG)
history_append(f'{dt_now()} LOADING KEYS...OK\n', DIAG)

connect_button_clicked()
message_box.focus()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
