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
if not os.path.exists(SERVER_PATH):
    os.makedirs(SERVER_PATH)

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
        print(data)
        data = data.split("@")
        print(data)
        cmd = data[0]

        if cmd == "HELP":
            send_data = "OK@"
            send_data += "LIST: Lists all files currently in the server.\n"
            send_data += "UPLOAD <path>: Uploads a new file to the server.\n"
            send_data += "DELETE <filename>: Deletes a file from the server.\n"
            send_data += "LOGOUT: Disconnects from the server.\n"
            send_data += "HELP: Displays all client commands for the server.\n"

            conn.send(send_data.encode(FORMAT))

        elif cmd == "LOGOUT":
            break

        elif cmd == "LIST":
            files = os.listdir(SERVER_PATH)
            send_data = "OK@"

            if len(files) == 0:
                send_data += "The server currenly has no files."
            else:
                send_data += "\n".join(f for f in files)
            conn.send(send_data.encode(FORMAT))

        elif cmd == "UPLOAD":
            name = data[1]
            text = data[2]

            filepath = os.path.join(SERVER_PATH, name)
            with open(filepath, "w") as f:
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


    print(f"[CONNECTION TERMINATED] USER: {addr} has disconnected.")

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