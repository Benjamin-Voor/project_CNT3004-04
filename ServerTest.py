# TODO: Collect and analyze performance metrics like upload/download time and transfer rate.
    # Maybe import time or tqdm.
    # FTP is not permitted.
# TODO: cmd "DOWNLOAD"
    # "UPLOAD" contents of file, not just its name.
# TODO: username/password authentication
# TODO: support pics & vids
# TODO: cmd mkdir
# TODO: cmd ls
# TODO: unknown cmd (Add else statement?)

import os
import socket
import threading
import hashlib
import logging

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4450 # Make sure the port matches with the server
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server_data"

### Ensures that the server data path exists
if not os.path.exists(SERVER_PATH):
    os.makedirs(SERVER_PATH)

logger = logging.getLogger('my logger')
logger.setLevel(logging.DEBUG)

### Handles incoming clients to the server
def handle_client (conn,addr):

    print(f"[CONNECTION ESTABLISHED] USER: {addr} has connected.")

    access_granted, received_username = authentication(conn)

    while access_granted and received_username:
        cmd, data = receive_from_client(conn)

        if cmd == "HELP":
            send_data = "OK@"
            send_data += "LIST: Lists all files currently in the server.\n"
            send_data += "UPLOAD <path>: Uploads a new file to the server.\n" # Note: Include 'client_data/' at the start and file extension at the end.
            send_data += "DELETE <filename>: Deletes a file from the server.\n" # Do not include file extension
            send_data += "LOGOUT: Disconnects from the server.\n"
            send_data += "HELP: Displays all client commands for the server.\n"
            send_data += "MKDIR: Create a new directory recursively. That means while making leaf directory if any intermediate-level directory is missing, MKDIR will create them all (separated by \'/\')."
            send_data += "RMDIR: Remove an old directory recursively."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "LIST":
            files = os.listdir(SERVER_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server currently has no files."
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            name = data[1]
            text = data[2]
            filepath = os.path.join(SERVER_PATH, name)
            with open(filepath, "wb") as f:
                f.write(text)

            send_data = "OK@File has been successfully uploaded."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_PATH)
            send_data = "OK@"
            filename = data[1]

            if len(files) == 0:
                send_data += "The server has no files."
            else:
                if filename in files:
                    os.remove(f"{SERVER_PATH}/{filename}")
                    send_data += "File has been successfully deleted."
                else:
                    send_data += "Error: file does not exist."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "MKDIR":
            print("Nope, that\'s not implemented yet!")
            continue

        else:
            send_data = "OK@"
            send_data += "Unknown command."
            conn.send(send_data.encode(FORMAT))

    print(f"[CONNECTION TERMINATED] USER: {addr} has disconnected.")


def authentication(conn):
    username = "username"
    password = "password"

    # username
    conn.send("UNAUTHENTICATED@Enter username (no spaces)".encode(FORMAT))
    received_username: bool = False
    hash_username = hashlib.new('sha256', username.encode(FORMAT)).hexdigest()  # encryption
    while not received_username:
        cmd, data = receive_from_client(conn)
        if cmd == hash_username:
            received_username = True
            break  # go to entering password
        elif cmd == "LOGOUT":
            break  # disconnect
        else:
            conn.send("UNAUTHENTICATED@Wrong username. Access denied!".encode(FORMAT))

    # password
    conn.send("UNAUTHENTICATED@Enter password (no spaces)".encode(FORMAT))
    # Source: Geeks for Geeks. https://www.geeksforgeeks.org/sha-in-python/.
    access_granted: bool = False
    hash_password = hashlib.new('sha256', password.encode(FORMAT)).hexdigest()  # encryption
    while not access_granted and received_username:
        cmd, data = receive_from_client(conn)
        if cmd == hash_password:  # cmd is already hashed.
            conn.send("OK@Welcome to the server!".encode(FORMAT))
            access_granted = True
            break
        elif cmd == "LOGOUT":
            break
        else:
            conn.send("UNAUTHENTICATED@Wrong password. Access denied!".encode(FORMAT))
    return access_granted, received_username


def receive_from_client(conn):
    data = conn.recv(SIZE).decode(FORMAT)
    data = data.split("@")
    cmd = data[0]
    return cmd, data


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"Server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()

if __name__ == "__main__":
    main()