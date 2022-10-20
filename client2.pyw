#!/usr/bin/python3

import socket
import _thread
import os
import sys
from funcs import dt_now, load_keys, send_encrypted, encrypt, decrypt, sign, verify, send, receive
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

HOST = '127.0.0.1'
PORT = 9999
NICKNAME = os.path.basename(sys.argv[0]).split(sep='.', maxsplit=1)[0]
SERVER = 'SERVER'
DIAG = 'DIAG'


def receive_data():
    """Receive, verify signature and decrypt messages from server"""
    global connected
    while True:
        try:
            data = receive(sock)
        except (ConnectionResetError, ConnectionAbortedError) as error:
            sock.close()
            connected = False
            history_append(f'{dt_now()} DISCONNECTED: {error.strerror}\n', DIAG)
            header_bar.props.subtitle = 'DISCONNECTED'
            break
        else:
            sender_nickname = data[0:512]
            sender_nickname = decrypt(sender_nickname, privkey)
            message = data[512:1024]
            signature = data[1024:1536]
            if verify(message, signature, contact_pubkey[sender_nickname]):
                message = decrypt(message, privkey)
                history_append(f'{dt_now()} <{sender_nickname}> {message}\n', sender_nickname)


def connect_button_clicked(obj=None):
    global sock, connected
    if not connected:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        history_append(f'{dt_now()} /connect\n{dt_now()} CONNECTING to {HOST}:{PORT} as <{NICKNAME}>...\n', DIAG)
        try:
            sock.connect((HOST, PORT))
        except ConnectionRefusedError as error:
            sock.close()
            connected = False
            history_append(f'{dt_now()} NOT CONNECTED: {error.strerror}\n', DIAG)
            header_bar.props.subtitle = 'NOT CONNECTED'
        else:
            send_encrypted(sock, NICKNAME, server_pubkey)
            message = receive(sock).decode('utf8')
            history_append(f'{dt_now()} {message}\n', DIAG)
            if message == 'CONNECTED':
                _thread.start_new_thread(receive_data, ())
                connected = True
                header_bar.props.subtitle = 'CONNECTED'
            else:
                sock.close()
                connected = False


def disconnect_button_clicked(obj=None):
    global connected
    if connected:
        sock.close()
        connected = False
        history_append(f'{dt_now()} /exit\n', DIAG)
        message_buffer.set_text('')


def send_button_clicked(obj=None):
    global OPPONENT_NICKNAME, connected
    message_textview.grab_focus()
    message = message_buffer.get_text(*message_buffer.get_bounds(), False)[:300]  # limit message to 300 symbols
    if connected and len(message) > 0 and OPPONENT_NICKNAME != DIAG:
        message_buffer.set_text('')
        message_split = message.split(maxsplit=1)
        match message_split:
            case ['/connect']:
                connect_button_clicked()
            case ['/quit' | '/exit']:
                disconnect_button_clicked()
            case ['/opponent', nickname]:
                OPPONENT_NICKNAME = nickname
                history_append(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
            case _:
                if message[0] == '@' and len(message_split) == 1:
                    OPPONENT_NICKNAME = message[1:]
                    history_append(f'{dt_now()} {message}\n{dt_now()} OPPONENT SET TO <{OPPONENT_NICKNAME}>\n')
                    message_buffer.set_text('')
                else:
                    history_append(f'{dt_now()} <{NICKNAME}> {message}\n')
                    nickname = encrypt(OPPONENT_NICKNAME, server_pubkey)
                    message = encrypt(message, contact_pubkey[OPPONENT_NICKNAME])
                    signature = sign(message, privkey)
                    data = nickname + message + signature
                    send(sock, data)


def ctrl_enter_pressed(obj, key):
    if key.hardware_keycode == 13 and key.get_state() == Gdk.ModifierType.CONTROL_MASK:
        send_button_clicked()


def contact_selected(obj, button):
    global OPPONENT_NICKNAME
    OPPONENT_NICKNAME = stack.get_visible_child_name()


def history_append(s, *args):
    """Append message to history TextView and history file"""
    message_buffer.set_text('')
    nickname = args[0] if len(args) == 1 else OPPONENT_NICKNAME
    contact_history[nickname].insert(contact_history[nickname].get_bounds()[1], s)
    with open(f'history_{NICKNAME}/{nickname}.txt', mode='a') as f:
        f.write(s)


sock = None
connected = False
contact_history = {}

"""GUI init"""
window = Gtk.Window()
window.set_default_size(800, 600)
window.set_resizable(False)
window.set_position(Gtk.WindowPosition.CENTER)
window.connect('destroy', Gtk.main_quit)

grid = Gtk.Grid()
window.add(grid)

header_bar = Gtk.HeaderBar()
header_bar.set_show_close_button(True)
header_bar.props.title = f'RSA-chat <{NICKNAME}>'
window.set_titlebar(header_bar)

box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
Gtk.StyleContext.add_class(box.get_style_context(), 'linked')
connect_button = Gtk.Button.new_from_icon_name('gtk-connect', Gtk.IconSize.MENU)
connect_button.connect('clicked', connect_button_clicked)
box.add(connect_button)
disconnect_button = Gtk.Button.new_from_icon_name('gtk-disconnect', Gtk.IconSize.MENU)
disconnect_button.connect('clicked', disconnect_button_clicked)
box.add(disconnect_button)
settings_button = Gtk.Button.new_from_icon_name('gtk-preferences', Gtk.IconSize.MENU)
box.add(settings_button)
header_bar.pack_start(box)

stack = Gtk.Stack()
stack.set_hexpand(True)
stack.set_vexpand(True)
grid.attach(stack, 1, 0, 6, 1)

contacts_sidebar = Gtk.StackSidebar()
contacts_sidebar.set_stack(stack)
contacts_sidebar.set_size_request(120, 0)
contacts_sidebar.connect('button-release-event', contact_selected)
grid.attach(contacts_sidebar, 0, 0, 1, 3)

separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
grid.attach(separator, 1, 1, 6, 1)

message_buffer = Gtk.TextBuffer()
message_textview = Gtk.TextView(buffer=message_buffer)
message_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
message_textview.set_size_request(560, 55)
message_textview.set_border_width(3)
message_textview.connect('key-press-event', ctrl_enter_pressed)
grid.attach(message_textview, 1, 2, 5, 1)

send_button = Gtk.Button.new_from_icon_name('gtk-ok', Gtk.IconSize.BUTTON)
send_button.set_border_width(3)
send_button.set_size_request(55, 55)
send_button.connect('clicked', send_button_clicked)
grid.attach(send_button, 6, 2, 1, 1)

"""Loading keys"""
privkey, contact_pubkey = load_keys(NICKNAME)
server_pubkey = contact_pubkey[SERVER]

"""Loading history"""
for nickname in (DIAG, *contact_pubkey.keys()):
    contact_history[nickname] = Gtk.TextBuffer()
    try:
        with open(f'history_{NICKNAME}/{nickname}.txt', mode='r') as f:
            contact_history[nickname].set_text(f.read())
    except FileNotFoundError:
        contact_history[nickname].set_text('')

    history_textview = Gtk.TextView(buffer=contact_history[nickname])
    history_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
    history_textview.set_editable(False)
    history_textview.set_cursor_visible(False)
    history_textview.set_border_width(3)

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.add(history_textview)

    stack.add_titled(scrolled_window, nickname, nickname)

OPPONENT_NICKNAME = DIAG

history_append(f'{HOST=}\n{PORT=}\n{NICKNAME=}\n{dt_now()} STARTING CLIENT...\n', DIAG)
history_append(f'{dt_now()} LOADING KEYS...OK\n', DIAG)

connect_button_clicked()
message_textview.grab_focus()
window.show_all()
Gtk.main()
