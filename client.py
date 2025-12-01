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
    messages.append(string)

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
    msg_type = msg.get("tffp").get("type")
    body = msg.get("tffp").get("body")

    if msg_type == "good":
        prepend_print(f"[SUCCESS] {body}")
    elif msg_type == "moot":
        prepend_print(f"[ERROR] {body}")
    elif msg_type == "hoot":
        prepend_print(f"[UPDATE] {body}")
    else:
        prepend_print(f"[CLIENT] Unknown server message: {msg}")


def main():


    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 3535


    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    print("\x1b[2JConnected to server.")

    # Start receiving thread
    threading.Thread(target=listen_for_messages, args=(sock,), daemon=True).start()

    # Command loop
    while True:

        cmd = input("> ").strip().lower()


        if cmd=="login":
            username = input("Username: ").strip()
            send_msg(sock, make_login_request(username))

        elif cmd=="signup":
            username = input("Username: ").strip()
            send_msg(sock, make_sign_up_request(username))

        elif cmd == "join":
            group = "public"
            send_msg(sock, make_join_request(group))
            #gives user a list of the members of the group when joining
            send_msg(sock, make_group_users_request(group))


        elif cmd == "leave":
            group = "public"
            send_msg(sock, make_leave_request(group))

        elif cmd == "post":
            group = "public"
            subject = input("Subject: ").strip()
            content = input("Content: ").strip()
            send_msg(sock, make_new_post_request(group, subject, content))

        elif cmd == "content":
            group = "public"
            post_id = int(input("Post ID: ").strip())
            send_msg(sock, make_content_request(group, post_id))

        elif cmd == "users":
            group = "public"
            send_msg(sock, make_group_users_request(group))


        elif cmd == "quit":
            send_msg(sock, make_quit_request())
            print("Closing client...")
            break

        #after this point is the part 2 commands
        #most are the same as part one commands but take input for the group rather than assuming
        #the user wishes to use the public group.

        elif cmd== "groups":
            send_msg(sock, make_groups_request())

        # group join takes a specific group name and joins that group
        elif cmd == "groupjoin":
            group = input("Group: ").strip()
            send_msg(sock, make_join_request(group))
            # gives user a list of the members of the group when joining
            send_msg(sock, make_group_users_request(group))

        elif cmd == "groupleave":
            group = input("Group: ").strip()
            send_msg(sock, make_leave_request(group))

        elif cmd == "grouppost":
            group = input("Group: ").strip()
            subject = input("Subject: ").strip()
            content = input("Content: ").strip()
            send_msg(sock, make_new_post_request(group, subject, content))

        elif cmd == "groupcontent":
            group = input("Group: ").strip()
            post_id = int(input("Post ID: ").strip())
            send_msg(sock, make_content_request(group, post_id))

        elif cmd == "groupusers":
            group = input("Group: ").strip()
            send_msg(sock, make_group_users_request(group))

        else:
            print("Commands: signup, login, groups, join/groupJoin, leave/groupLeave, post/groupPost, "
                  "\n content/groupContent, users/groupUsers, quit")

    sock.close()


if __name__ == "__main__":
    main()
