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
PORT = 4450 # Make sure the port matches with the server
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server_data"

### Ensures that the server data path exists
if not os.path.exists(SERVER_PATH):
    os.makedirs(SERVER_PATH)
# Equivalent to `os.makedirs(SERVER_PATH, exist_ok=True)`


logger = logging.getLogger('my logger')
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

### Handles incoming clients to the server
def handle_client (conn,addr):

    print(f"[CONNECTION ESTABLISHED] USER: {addr} has connected.")

    access_granted, received_username = authentication(conn)

    while access_granted and received_username:
        try:
            cmd, data = receive_from_client(conn)
        except ConnectionResetError:
            break

        if cmd == "HELP":
            send_data = "OK@"
            send_data += "LIST: Lists all files currently in the server.\n"
            send_data += "UPLOAD <path>: Uploads a new file to the server.\n" # Note: Include 'client_data/' at the start and file extension at the end.
            send_data += "DELETE <filename>: Deletes a file from the server.\n" # Do not include file extension
            send_data += "LOGOUT: Disconnects from the server.\n"
            send_data += "HELP: Displays all client commands for the server.\n"
            send_data += "MKDIR: Create a new directory recursively. That means while making leaf directory if any intermediate-level directory is missing, MKDIR will create them all (separated by \'/\').\n"
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
            try:
                name = data[1]
                text = data[2]
            except IndexError as e:
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e

            logging.info("Valid command. Writing file...")
            filepath = os.path.join(SERVER_PATH, name)
            with open(filepath, "wb") as f:
                f.write(text)

            logging.info("Uploaded file \"{filename}\"")
            send_data = "OK@File has been successfully uploaded."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DELETE":
            files = os.listdir(SERVER_PATH)
            send_data = "OK@"
            try:
                filename = data[1]
            except IndexError as e:
                logging.debug(f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.")
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e

            if len(files) == 0:
                send_data += "The server has no files."
            else:
                if filename in files:
                    os.remove(f"{SERVER_PATH}/{filename}")
                    logging.info("Deleted file \"{filename}\"")
                    send_data += "File \"{filename}\" has been successfully deleted."
                else:
                    send_data += f"Error: file \"{filename}\" does not exist."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "MKDIR":
            send_data = "OK@"
            # Leaf directory
            try:
                name = data[1]
            except IndexError as e:
                logging.debug(f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.")
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e
            filepath = os.path.join(SERVER_PATH, name)
            try:
                os.makedirs(filepath, exist_ok=False)
            except OSError as e:
                send_data += f"Directory \"{name}\" already exists {e}"
                conn.send(send_data.encode(FORMAT))
                continue
            logging.info("Added directory \"{name}\"")
            send_data += f"Directory \"{name}\" has been successfully created"
            conn.send(send_data.encode(FORMAT))

        elif cmd == "RMDIR":
            send_data = "OK@"
            # Leaf directory
            try:
                name = data[1]
            except IndexError as e:
                logging.debug(f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.")
                raise IndexError(f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation.", f"Fix the try-except block for \"{cmd}\" command in ClientTest.py.") from e

            filepath = os.path.join(SERVER_PATH, name)
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
            send_data = "OK@"
            send_data += f"Unknown command \'{cmd}\'."
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
    # logging.info("Data received: ", data) # causes logging errors
    data = data.split("@")
    cmd = data[0]
    # logging.info("Data converted to: ", cmd, data) # causes logging errors
    # logging.info("Command received:", cmd) # causes errors
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