"""Feel free to delete me this is just for tests not actually part of the assignment
"""

import socket
import json

from message_functions import *

def setup():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 3535))

def sign_up(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 3535))

    sock.send((json.dumps(make_sign_up_request(name)) + "\n").encode("utf-8"))
    sock.send((json.dumps(make_join_request("public")) + "\n").encode("utf-8"))

    recv_to_wait_for_a_response = sock.recv(4000)
    recv_to_wait_for_a_response = sock.recv(4000)

