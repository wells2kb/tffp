import socket
import json
import threading
import sys
from message_functions import *

messages = []

#sends message to server
def send_msg(sock, msg_dict):
    """Convert dict → JSON string → send."""
    data = json.dumps(msg_dict)
    sock.sendall(data.encode() + b"\n")  # newline helps with framing

def prepend_print(string):
    MAGIC_NUMBER = 12
    messages.extend(string.split("\n"))

    diff = max(0, MAGIC_NUMBER - len(messages))
    for _ in range(MAGIC_NUMBER - diff + 1):
        sys.stdout.write("\x1b[F\x1b[K")

    sys.stdout.write("\x1b[2J")

    for message in messages[-MAGIC_NUMBER:]:
        print(message)

    print("")
    sys.stdout.write("> ")
    sys.stdout.flush()


#constantly running, should handle messages when it recieves them
def listen_for_messages(sock):
    with sock.makefile() as sock_file:
        for line in sock_file:
            try:
                msg = json.loads(line)
                handle_server_message(msg)
            except json.JSONDecodeError:
                prepend_print("[CLIENT] Could not parse message:" + msg)


#handles message by outputting appropriate updates.
def handle_server_message(msg):
    """Add message type to server message content"""
    # prepend message depending on type
    msg_type = msg.get("tffp").get("type")
    # get message content
    body = msg.get("tffp").get("body")

    if msg_type == "good":
        prepend_print(f"[SUCCESS] {body}")
    elif msg_type == "moot":
        prepend_print(f"[ERROR] {body}")
    elif msg_type == "hoot":
        match body["command"]:
            case "post":
                prepend_print(f"[UPDATE] New post in '{body['group']}': {body['args']}")
            case "join":
                prepend_print(f"[UPDATE] '{body['args']}' just joined '{body['group']}'")
            case "leave":
                prepend_print(f"[UPDATE] '{body['args']}' just left '{body['group']}'")
            case _:
                prepend_print(f"[UPDATE] {body}")
    else:
        prepend_print(f"[CLIENT] Unknown server message: {msg}")
   

def main():
    # connect sock and start listener
    sock, listener = None, None
    
    print("Please 'connect' to continue")

    # Command loop
    while True:
        cmd = input("> ").strip().lower()

        if sock is None and cmd != "connect" and cmd != "exit":
            # Must connect to a server before running other commands
            print("Connect to a server first.")
            continue

        if cmd == "connect":
            if sock is not None:
                print("Already connected.")
                continue
            
            # get IP and Port of a bulletin board server
            server_ip = input("IP or press 'ENTER' for the default: ")
            server_port = input("Port or press 'ENTER' for the default: ")
            if not server_ip: 
                server_ip = "127.0.0.1"
            if not server_port: 
                server_port = 3535
            
            try:
                # Connect to server
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server_ip, int(server_port)))
                print(f"\x1b[2JConnected to server IP={server_ip} Port={server_port}")
                print(f"Please 'signup' or 'login' to continue")
                
                # Start receiving thread
                listener = threading.Thread(target=listen_for_messages, args=(sock,), daemon=False)
                listener.start()
            except Exception as e:
                sock = None
                print(f"Connection failed with error: {e}")
            
        elif cmd=="login":
            # login with a given username
            username = input("Username: ").strip()
            send_msg(sock, make_login_request(username))

        elif cmd=="signup":
            # signup and login with a given username
            username = input("Username: ").strip()
            send_msg(sock, make_sign_up_request(username))

        elif cmd == "join":
            # join the public group
            group = "public"
            send_msg(sock, make_join_request(group))


        elif cmd == "leave":
            # leave the public group
            group = "public"
            send_msg(sock, make_leave_request(group))

        elif cmd == "post":
            # make a post to public group
            group = "public"
            subject = input("Subject: ").strip()
            content = input("Content: ").strip()
            send_msg(sock, make_new_post_request(group, subject, content))

        elif cmd == "content":
            # see content of message given a post ID in public group
            group = "public"
            post_id = int(input("Post ID: ").strip())
            send_msg(sock, make_content_request(group, post_id))

        elif cmd == "users":
            # list users in public group
            group = "public"
            send_msg(sock, make_group_users_request(group))

        elif cmd == "exit":
            print("Closing client...")
            if sock is None:
                # just exit, nothing to close
                break
            # Force listener to stop reading
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass

            sock.close()
            listener.join() # join threads for shutdown

        #after this point is the part 2 commands
        #most are the same as part one commands but take input for the group rather than assuming
        #the user wishes to use the public group.

        elif cmd== "groups":
            # list all groups
            send_msg(sock, make_groups_request())

        # group join takes a specific group name and joins that group
        elif cmd == "groupjoin":
            # join a given group
            group = input("Group: ").strip()
            send_msg(sock, make_join_request(group))

        elif cmd == "groupleave":
            # leave a given group
            group = input("Group: ").strip()
            send_msg(sock, make_leave_request(group))

        elif cmd == "grouppost":
            # make a post to a given group
            group = input("Group: ").strip()
            subject = input("Subject: ").strip()
            content = input("Content: ").strip()
            send_msg(sock, make_new_post_request(group, subject, content))

        elif cmd == "groupcontent":
            # get content of message in a given group and post id
            group = input("Group: ").strip()
            post_id = int(input("Post ID: ").strip())
            send_msg(sock, make_content_request(group, post_id))

        elif cmd == "groupusers":
            # get list of users in a group
            group = input("Group: ").strip()
            send_msg(sock, make_group_users_request(group))

        else:
            # if user enters invalid command, show list of valid commands 
            print("Commands: connect, signup, login, groups, join/groupJoin, leave/groupLeave, post/groupPost, "
                  "\n content/groupContent, users/groupUsers, exit")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
