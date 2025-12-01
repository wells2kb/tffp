import socket
import threading
import json
import random
import sys
from datetime import datetime
from dataclasses import dataclass, field

from message_functions import *

MAX_BYTES = 4096
HOST = '0.0.0.0'
PORT = 3535

class ThreadSafeList:
    def __init__(self):
        self._list = []
        self._lock = threading.Lock()

    def __enter__(self):
        self._lock.acquire()
        return self._list

    def __exit__(self, *args):
        self._lock.release()

    def __str__(self):
        with self._lock:
            string = str(self._list)
        return string.replace("'", '"')

    def get(self, index):
        with self._lock:
            value = self._list[index]
        return value

    def push(self, value):
        with self._lock:
            self._list.append(value)
            index = len(self._list) - 1
        return index 

    def delist(self, value):
        with self._lock:
            self._list.remove(value)

@dataclass
class GroupData:
    posts: ThreadSafeList = field(default_factory=ThreadSafeList)
    users: ThreadSafeList = field(default_factory=ThreadSafeList)

@dataclass
class Post:
    sender: str
    date: str
    subject: str
    content: str

@dataclass
class Client:
    socket: socket.SocketType
    username: str

# Groups aren't added/removed so no need for thread safety here
groups = {
    "public": GroupData(),
    "freeganism": GroupData(),
    "squatting": GroupData(),
    "anarchism": GroupData(),
    "churning": GroupData(),
    "super mario brothers 2": GroupData()
}
clients = ThreadSafeList()
# Keep names unqiue
names = ThreadSafeList()

def handle_client(client_socket, client_address):
        user = ""
        with client_socket.makefile('r') as socket_file:
            for line in socket_file:
                try:
                    tffp = json.loads(line)

                    message = tffp["tffp"]
                    body = message["body"]
                    command = body["command"]

                    group = body.get("group")
                    args = body.get("args")

                    # Only process seek messages from the client
                    if message["type"] == "seek":
                        response_message = make_deny_response("Command failed, try agian")
                        update_message = None

                        # Check if the user is member of the group in their request
                        is_member = False
                        if user and group:
                            with groups[group].users as users:
                                is_member = user in users
                        
                        if is_member:
                            match command:
                                case "post":
                                    subject = args["subject"]
                                    content = args["content"]
                                    assert type(subject) == str
                                    assert type(content) == str
                                    if subject == "" or content == "":
                                        raise ValueError("Subject/content must be non-empty string")

                                    date = datetime.now().strftime("%H:%M")
                                    post = Post(user, date, subject, content)
                                    post_id = groups[group].posts.push(post)

                                    response_message = make_accept_response("Post Success!")
                                    update_message = make_new_post_update(group, post_id, user, date, subject)

                                case "content":
                                    assert type(args) == int
                                    response_message = make_accept_response(groups[group].posts.get(args).content)

                                case "leave":
                                    groups[group].users.delist(user)
                                    response_message = make_accept_response("Left Group!")
                                    update_message = make_leave_update(group, user)

                                case "quit":
                                    #not using group to avoid confusion
                                    for g in groups:
                                        groups[g].users.delist(user)
                                    response_message = make_accept_response("Quit from message board")
                                    update_message = make_leave_update(group, user) #may need to make a different update_message for quitting



                                case "users":
                                    response_message = make_accept_response(str(groups[group].users))

                                case "groups":
                                    response_message=make_accept_response(str(list(groups.keys())))

                                case "join":
                                    response_message = make_deny_response("Already in that group")

                                case "login" | "sign_up":
                                    response_message = make_deny_response("You are already logged in")

                                case _:
                                    response_message = make_deny_response(f"Not a valid Command: '{command}'")

                        elif user:
                            # Else we are not already in the selected group
                            match command:
                                case "join":
                                    groups[group].users.push(user)
                                    response_message = make_accept_response("Joined Group!")
                                    update_message = make_join_update(group, user)
                                
                                case "login" | "sign_up":
                                    response_message = make_deny_response("You are already logged in")

                                case "groups":
                                    response_message = make_accept_response(str(list(groups.keys())))

                                case "quit":
                                    # not using group to avoid confusion
                                    for g in groups:
                                        groups[g].users.delist(user)
                                    response_message = make_accept_response("Quit from message board")
                                    update_message = make_leave_update(group,user)  # may need to make a different update_message for quitting

                                case _:
                                    response_message = make_deny_response(f"Must join Group: '{group}' before using the Command: '{command}'")

                        else:
                            # Not logged in
                            match command:
                                case "login":
                                    assert type(args) == str
                                    if args == "":
                                        raise ValueError("Username must be non-empty string")

                                    with names as name_list:
                                        if args in name_list:
                                            user = args
                                            clients.push(Client(client_socket, user))
                                            response_message = make_accept_response("You are logged in!")
                                        else:
                                            response_message = make_deny_response("Username not Found")

                                case "sign_up":
                                    assert type(args) == str
                                    if args == "":
                                        raise ValueError("Username must be non-empty string")

                                    with names as name_list:
                                        if args not in name_list:
                                            user = args
                                            name_list.append(user)
                                            clients.push(Client(client_socket, user))
                                            response_message = make_accept_response("You are signed up and logged in!")
                                        else:
                                            response_message = make_deny_response("Username already in use")

                                case _:
                                    response_message = make_deny_response("Not logged in :(")

                        client_socket.sendall((json.dumps(response_message) + "\n").encode('utf-8'))

                        if update_message:
                            with clients as client_list, groups[group].users as users:
                                for client in client_list:
                                    if client.username in users:
                                        try:
                                            client.socket.sendall((json.dumps(update_message) + "\n").encode('utf-8'))
                                        except ConnectionError:
                                            client_list.remove(client)


                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    line = exc_traceback.tb_lineno
                    client_socket.sendall((json.dumps(make_deny_response(f"{type(e).__name__} on line: {line}, '{e}'")) + "\n").encode('utf-8'))


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    client = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=client)
    thread.start()

