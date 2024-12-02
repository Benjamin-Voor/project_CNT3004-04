# TODO: Collect and analyze performance metrics like upload/download time and transfer rate.
    # Both server and client applications
    # Maybe import time or tqdm.
    # FTP is not permitted.
# TODO: cmd "DOWNLOAD"
    # "UPLOAD" contents of file, not just its name.
# TODO: username/password authentication
# TODO: support pics & vids
# TODO: cmd mkdir
# TODO: cmd ls
# TODO: unknown cmd (Add else statement?)
# TODO: "Continue" from unknown commands and from try-except blocks, rather than presently breaking out of them.
# TODO: Provide feedback to the user regarding the status of file transfers and operations.
# TODO: Performance Analysis: Conduct experiments to measure the system's performance under various load conditions. Analyze the collected data to identify bottlenecks and areas for optimization.
# TODO: Skip the security assessment. I don't know how to do that.
# TODO: comprehensive project report
# TODO: Add more python modules
    # Maybe add the stuff that both client and server have in common, like import statements and the logger.

import os
import socket
import threading
import hashlib
import logging

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4451 # Make sure the port matches with the server
ADDR = (IP, PORT)
SIZE = 65536
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

### Ensures that the server data path exists
if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)
# Equivalent to `os.makedirs(SERVER_PATH, exist_ok=True)`


logger = logging.getLogger('my logger')
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')
def list_directory_contents(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in dirs:
            file_list.append(os.path.relpath(os.path.join(root, name), directory) + '/')
        for name in files:
            file_list.append(os.path.relpath(os.path.join(root, name), directory))
    return file_list

### Handles incoming clients to the server
def handle_client (conn,addr):

    print(f"[NEW CONNECTION] {addr} connected.")

    access_granted, received_username = authentication(conn)

    while access_granted and received_username:
        try:
            cmd, data = receive_from_client(conn)
            if not data:
                break  # Don't check if-statements until data is received.
        except ConnectionResetError:
            break

        if cmd == "HELP":
            if not (access_granted and received_username):
                send_data = "OK@"
                send_data += "LOGOUT: Disconnects from the server.\n"
            else:
                send_data = "OK@"
                send_data += "LIST_SERVER: Lists all files currently in the server.\n"
                send_data += "UPLOAD <path>: Uploads a new file to the server.\n" # Note: Include 'client_data/' at the start and file extension at the end.
                send_data += "DELETE <filename>: Deletes a file from the server.\n" # Do not include file extension
                send_data += "LOGOUT: Disconnects from the server.\n"
                send_data += "HELP: Displays all client commands for the server.\n"
                send_data += "MKDIR: Create a new directory recursively. That means while making leaf directory if any intermediate-level directory is missing, MKDIR will create them all (separated by \'/\').\n"
                send_data += "RMDIR: Remove an old directory recursively."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "LIST_SERVER":
            files = list_directory_contents(SERVER_DATA_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            if len(data) >= 3:
                name = data[1]
                file_size = int(data[2])
                filepath = os.path.join(SERVER_DATA_PATH, name)

                logging.info("Valid command. Writing file...")
                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < file_size:
                        chunk = conn.recv(SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                logging.info("Uploaded file \"{filename}\"")
                send_data = "OK@File uploaded successfully."
                conn.send(send_data.encode(FORMAT))
            else:
                send_data = "ERROR@Invalid upload data."
                conn.send(send_data.encode(FORMAT))

        elif cmd == "DOWNLOAD":
            filename = data[1]
            filepath = os.path.join(SERVER_DATA_PATH, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                conn.send(f"OK@{file_size}".encode(FORMAT))
                with open(filepath, "rb") as f:
                    bytes_sent = 0
                    while bytes_sent < file_size:
                        chunk = f.read(SIZE)
                        conn.send(chunk)
                        bytes_sent += len(chunk)
            else:
                send_data = "ERROR@File not found."
                conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_DATA_PATH)
            send_data = "OK@"
            try:
                filename = data[1]
            except IndexError as e:
                logging.debug(f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.")
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    os.remove(f"{SERVER_DATA_PATH}/{filename}")
                    logging.info("Deleted file \"{filename}\"")
                    send_data += "File deleted successfully."
                else:
                    send_data += "File not found."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "MKDIR":
            if len(data) >= 2:
                dir_name = data[1]
                dir_path = os.path.join(SERVER_DATA_PATH, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    logging.info("Added directory \"{name}\"")
                    send_data = f"OK@Directory {dir_name} created successfully."
                else:
                    send_data = f"ERROR@Directory {dir_name} already exists."
                conn.send(send_data.encode(FORMAT))
            else:
                send_data = "ERROR@Invalid directory name."
                conn.send(send_data.encode(FORMAT))

        elif cmd == "RMDIR":
            send_data = "OK@"
            # Leaf directory
            try:
                name = data[1]
            except IndexError as e:
                logging.debug(f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.")
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e

            filepath = os.path.join(SERVER_DATA_PATH, name)
            try:
                os.rmdir(filepath)
            except OSError as e:
                send_data += f"Directory \"{name}\" cannot be removed {e}"
                conn.send(send_data.encode(FORMAT))
                continue
            logging.info("Removed directory \"{name}\"")
            send_data += f"Directory \"{name}\" has been successfully removed!"
            conn.send(send_data.encode(FORMAT))

        else:
            send_data = "ERROR@Unknown command."
            conn.send(send_data.encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()


def authentication(conn):
    # Source: Geeks for Geeks. https://www.geeksforgeeks.org/sha-in-python/.
    username = "username"
    password = "password"

    ### username
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

    ### password
    conn.send("UNAUTHENTICATED@Enter password (no spaces)".encode(FORMAT))
    access_granted: bool = False
    hash_password = hashlib.new('sha256', password.encode(FORMAT)).hexdigest()  # encryption
    while not access_granted and received_username:
        cmd, data = receive_from_client(conn)
        if cmd == hash_password:  # cmd is already hashed.
            conn.send("OK@Welcome to the File Server.".encode(FORMAT))
            access_granted = True
            break
        elif cmd == "LOGOUT":
            break
        else:
            conn.send("UNAUTHENTICATED@Wrong password. Access denied!".encode(FORMAT))
    return access_granted, received_username


def receive_from_client(conn):
    data = conn.recv(SIZE).decode(FORMAT)
    # logging.info("Data received: ", data) # causes logging errors
    data = data.split("@")
    cmd = data[0]
    # logging.info("Data converted to: ", cmd, data) # causes logging errors
    # logging.info("Command received:", cmd) # causes errors
    return cmd, data


def main():
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target=handle_client, args=(conn, addr)) ## assigning a thread for each client
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
