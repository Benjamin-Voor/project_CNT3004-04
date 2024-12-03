import socket
import threading
import metrics
from some_server_methods import *

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4451 # Make sure the port matches with the server
ADDR = (IP, PORT)

### The block below is already defined in some_server_methods.py
    # SIZE = 65536
    # FORMAT = "utf-8"
    # SERVER_DATA_PATH = "server_data"
    # USERNAME = "username with spaces"
    # PASSWORD = "password with spaces"


### Ensures that the server data path exists
if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)
# Equivalent to `os.makedirs(SERVER_DATA_PATH, exist_ok=True)`


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

    access_granted, received_username = authentication(conn) # some_server_methods.py

    while access_granted and received_username:
        try:
            cmd, data = receive_from_client(conn)
            if not (cmd and data):
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
                send_data += " " # "Try again" was kind of confusing, because ¿what if they shouldn't perform the same incorrect command twice?
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
                if len(data) >= 3:
                    logging.info(f"Response time for UPLOAD: {response_time:.2f} seconds")
                else:
                    logging.info(f"Response time for failed UPLOAD: {response_time:.2f} seconds")

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
                mkdir(conn, data) # some_server_methods.py


            case "RMDIR":

                rmdir(cmd, conn, data) # some_server_methods.py

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
