# Usability Instructions
Commands for part 1: connect, signup, login, groups, join, leave, post, content, users, quit

Commands for part 2: groupJoin, groupLeave, groupPost, groupContent, groupUsers

### Part 1 commands
- connect: enter IP address and Port number of a server and connect to it
- signup: enter username to sign up and log in
- login: enter valid username to log in
- groups: list available groups to join
- join: join the public group
- leave: leave the public group
- post: post a message with a subject and content to the public group
- content: see the content of a specific message ID in the public group
- users: list the usernames who are in the public group
- quit: leave groups, log out, and close connection with server
### Part 2 commands
- groupJoin: join a group
- groupLeave: leave a group
- groupPost: post to a given group
- groupContent: see the message content of a given post in a given group
- groupUsers: list thet usernames who are in a given group

## Getting started
1. run `python client.py`
2. Connect to server by entering command `connect`
3. Enter `127.0.0.1` for IP
4. Enter `3535` for Port
5. Signup using `signup` command and any username
6. Join the public server using `join` command

# Handling Major Issues
1. Client would error with a Fatal Python error after running `quit`. This is because the listener
daemon threads would get killed abruptly when the main thread ended. The solution was to
make the listener threads non-daemon and join the threads before the main thread ended, allowing the
threads to finish and exit.
2. Client would hang after running `quit` command even though we closed the socket,
 joined the listener threads, and broke the while loop. This was because the listener 
 thread was blocked, still waiting for data from the socket. We fixed this by adding 
 sock.shutdown(socket.SHUT_RDWR), which terminates the socket connection and forces the 
 listener thread to terminate, allowing the code to progress.