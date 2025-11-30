import socket
import json
import threading
from message_functions import *


#sends message to server
def send_msg(sock, msg_dict):
    """Convert dict → JSON string → send."""
    data = json.dumps(msg_dict)
    sock.sendall(data.encode() + b"\n")  # newline helps with framing


#constantly running, should handle messages when it recieves them
def listen_for_messages(sock):
    buffer = ""
    while True:
        try:
            chunk = sock.recv(4096).decode()
            if not chunk:
                print("Server closed connection.")
                break

            buffer += chunk

            # Process full messages separated by newlines
            while "\n" in buffer:
                raw, buffer = buffer.split("\n", 1)
                if raw.strip() == "":
                    continue

                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    print("[CLIENT] Could not parse message:", raw)
                    continue

                # Handle message
                handle_server_message(msg)

        except ConnectionResetError:
            print("Connection lost.")
            break


#handles message by outputting appropriate updates.
def handle_server_message(msg):
    msg_type = msg.get("type")

    if msg_type == "good":
        print(f"[SUCCESS] {msg.get('body')}")
    elif msg_type == "moot":
        print(f"[ERROR] {msg.get('body')}")
    elif msg_type == "hoot":
        print(f"[UPDATE] {msg.get('body')}")
    else:
        print("[CLIENT] Unknown server message:", msg)





def main():
    #in the final iteration we need a connect command so these will be removed in favor of that
    #connect command will replace signup/login
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 3535

    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server.")

    # Start receiving thread
    threading.Thread(target=listen_for_messages, args=(sock,), daemon=True).start()

    # Command loop
    while True:
        cmd = input("> ").strip().lower()

        #TODO: convert to connect command; sends same message but does so after connecting to the server
        #(preferably done after we confirm the code works w/ hardcoded server data above so we can test that easily)
        if cmd == "signup" or cmd=="login":
            username = input("Username: ").strip()
            send_msg(sock, make_login_request(username))


        elif cmd == "join":
            group = "public"
            send_msg(sock, make_join_request(group))


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


        #TODO: modify so that the server gets notified/removes user from ALL groups they are a part of
        elif cmd == "quit":
            print("Closing client...")
            break

        #after this point is the part 2 commands

        #TODO: implement this in message_functions
        elif cmd== "groups":
            pass



        # group join takes a specific group name and joins that group
        elif cmd == "groupjoin":
            group = input("Group: ").strip()
            send_msg(sock, make_join_request(group))

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
            print("Commands: signup, login, join/groupJoin, leave/groupLeave, post/groupPost, "
                  "\n content/groupContent, users/groupUsers, quit")

    sock.close()


if __name__ == "__main__":
    main()