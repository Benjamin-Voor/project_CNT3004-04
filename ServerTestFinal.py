# TODO: Provide feedback to the user regarding the status of file transfers and operations.
# TODO: Performance Analysis: Conduct experiments to measure the system's performance under various load conditions. Analyze the collected data to identify bottlenecks and areas for optimization.
# TODO: Skip the security assessment. I don't know how to do that.
# TODO: comprehensive project report

import os
import socket
import threading
import hashlib
import logging
import metrics

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

        match cmd:

            case "HELP":
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
                    send_data += "RMDIR: Remove an old directory, but not recursively."
                conn.send(send_data.encode(FORMAT))


            case "ERROR":
                send_data = "ERROR@"
                send_data += "Try again."
                conn.send(send_data.encode(FORMAT))


            case "LOGOUT":
                break


            case "LIST_SERVER":
                files = list_directory_contents(SERVER_DATA_PATH)
                send_data = "OK@"

                if len(files) == 0:
                    send_data += "The server directory is empty"
                else:
                    send_data += "\n".join(f for f in files)
                conn.send(send_data.encode(FORMAT))


            case "UPLOAD":
                metrics.start_response()  # Record start time of response
                if len(data) >= 3:
                    name = data[1]
                    file_size = int(data[2])
                    filepath = os.path.join(SERVER_DATA_PATH, name)
                    logging.info("Valid command. Writing file...")
                    metrics.start_upload()  # Record start time of upload
                    with open(filepath, "wb") as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = conn.recv(SIZE)
                            if not chunk:
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                    metrics.end_upload()  # Record end time of upload
                    upload_time = metrics.get_upload_time()
                    rate = metrics.calculate_rate(file_size, upload_time)
                    metrics.print_times()  # Print start and end times
                    logging.info(
                        f"Uploaded file \"{name}\" in {upload_time:.2f} seconds at an average rate of {rate:.2f} MB/s")
                    send_data = "OK@File uploaded successfully."
                else:
                    send_data = "ERROR@Invalid upload data."
                conn.send(send_data.encode(FORMAT))
                metrics.end_response()  # Record end time of response
                response_time = metrics.get_response_time()
                logging.info(f"Response time for UPLOAD: {response_time:.2f} seconds")


            case "DOWNLOAD":
                metrics.start_response()  # Record start time of response
                filename = data[1]
                filepath = os.path.join(SERVER_DATA_PATH, filename)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    conn.send(f"OK@{file_size}".encode(FORMAT))
                    metrics.start_download()  # Record start time of download
                    with open(filepath, "rb") as f:
                        bytes_sent = 0
                        while bytes_sent < file_size:
                            chunk = f.read(SIZE)
                            conn.send(chunk)
                            bytes_sent += len(chunk)
                    metrics.end_download()  # Record end time of download
                    download_time = metrics.get_download_time()
                    rate = metrics.calculate_rate(file_size, download_time)
                    metrics.print_times()  # Print start and end times
                    logging.info(
                        f"Downloaded file \"{filename}\" in {download_time:.2f} seconds at an average rate of {rate:.2f} MB/s")
                else:
                    send_data = "ERROR@"
                    send_data += "File not found."
                    conn.send(send_data.encode(FORMAT))
                metrics.end_response()  # Record end time of response
                response_time = metrics.get_response_time()
                logging.info(f"Response time for DOWNLOAD: {response_time:.2f} seconds")


            case "DELETE":
                files = os.listdir(SERVER_DATA_PATH)
                send_data = "OK@"
                if len(data) == 2:
                    filename = data[1]
                else:
                    invalid_input(cmd, conn)

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


            case "MKDIR":
                if len(data) >= 2:
                    dir_name = data[1]
                    dir_path = os.path.join(SERVER_DATA_PATH, dir_name)
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                        logging.info("Added directory \"{name}\"")
                        send_data = f"OK@Directory '{dir_name}' created successfully."
                    else:
                        send_data = f"ERROR@Directory {dir_name} already exists."
                    conn.send(send_data.encode(FORMAT))
                else:
                    send_data = "ERROR@Invalid directory name."
                    conn.send(send_data.encode(FORMAT))


            case "RMDIR":

                send_data = "OK@"
                try:
                    if len(data) >= 2:
                        name = data[1]
                    else:
                        raise IndexError("No directory name provided")
                    filepath = os.path.join(SERVER_DATA_PATH, name)
                    logging.debug(f"Attempting to remove directory: {filepath}")
                    # Ensure the directory exists
                    if not os.path.exists(filepath):
                        logging.debug(f"Directory not found: {filepath}")
                        send_data = f"ERROR@Directory \"{name}\" does not exist."
                        cmd = "ERROR"
                        # conn.send(send_data.encode(FORMAT)) # This is done in finally statement
                        continue
                    # Ensure the directory is empty
                    if os.listdir(filepath):
                        send_data = f"ERROR@Directory \"{name}\" is not empty."
                        cmd = "ERROR"
                        # conn.send(send_data.encode(FORMAT)) # # This is done in finally statement
                        continue
                    os.rmdir(filepath)
                    logging.info(f"Removed directory \"{name}\"")
                    send_data += f"Directory \"{name}\" has been successfully removed!"
                except IndexError as e:
                    send_data = f"ERROR@Invalid input for \"{cmd}\" command. {e}"
                    cmd = "ERROR"
                except OSError as e:
                    send_data += f"Directory \"{name}\" cannot be removed. {e}"
                    cmd = "ERROR"
                finally:
                    conn.send(send_data.encode(FORMAT))
            case _:
                send_data = "ERROR@"
                send_data += "Unknown command."
                conn.send(send_data.encode(FORMAT))




    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()


def invalid_input(cmd, conn):
    send_data = "ERROR@"
    send_data += f"Invalid input for \"{cmd}\" command. Enter \"HELP\" for correct implementation."
    conn.send(send_data.encode(FORMAT))
    return send_data


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
