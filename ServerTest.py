import os
import socket
import threading

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4451
ADDR = (IP, PORT)
SIZE = 65536
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

### Ensures that the server data path exists
if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)

def list_directory_contents(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in dirs:
            file_list.append(os.path.relpath(os.path.join(root, name), directory) + '/')
        for name in files:
            file_list.append(os.path.relpath(os.path.join(root, name), directory))
    return file_list

### Handles incoming clients to the server
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the File Server.".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        if not data:
            break # Don't check if-statements until data is received.
        data = data.split("@")
        cmd = data[0]

        if cmd == "LIST_SERVER":
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

                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < file_size:
                        chunk = conn.recv(SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
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
            filename = data[1]

            if len(files) == 0:
                send_data += "The server directory is empty"
            else:
                if filename in files:
                    os.remove(f"{SERVER_DATA_PATH}/{filename}")
                    send_data += "File deleted successfully."
                else:
                    send_data += "File not found."
            conn.send(send_data.encode(FORMAT))

        elif cmd == "MAKEDIR":
            if len(data) >= 2:
                dir_name = data[1]
                dir_path = os.path.join(SERVER_DATA_PATH, dir_name)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                    send_data = f"OK@Directory {dir_name} created successfully."
                else:
                    send_data = f"ERROR@Directory {dir_name} already exists."
                conn.send(send_data.encode(FORMAT))
            else:
                send_data = "ERROR@Invalid directory name."
                conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "HELP":
            send_data = "OK@"
            send_data += "LIST_SERVER or DIRS: List all the files and directories from the server.\n"
            send_data += "UPLOAD <path>: Upload a file to the server.\n"
            send_data += "DOWNLOAD <filename>: Download a file from the server.\n"
            send_data += "DELETE <filename>: Delete a file from the server.\n"
            send_data += "MAKEDIR <dirname>: Create a directory on the server.\n"
            send_data += "LOGOUT: Disconnect from the server.\n"
            send_data += "HELP: List all the commands."
            conn.send(send_data.encode(FORMAT))

        else:
            send_data = "ERROR@Unknown command."
            conn.send(send_data.encode(FORMAT))

    print(f"[DISCONNECTED] {addr} disconnected")
    conn.close()

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
