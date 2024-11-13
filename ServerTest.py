import os
import socket
import threading

IP = "10.221.82.245" ### gethostname()
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

### Ensures that the server data path exists
if not os.path.exists(SERVER_PATH):
    os.makedirs(SERVER_PATH)


### Handles incoming clients to the server
def handle_client (conn,addr):

    print(f"NEW CONNECTION: {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        send_data = "OK@"

        if cmd == "LOGOUT":
            break

        elif cmd == "TASK":
            send_data += "LOGOUT from the server.\n"
            conn.send(send_data.encode(FORMAT))

        ### "LIST" lists all files in the server directory
        elif cmd == "LIST":
            files = os.listdir(SERVER_PATH)
            response = "OK@" + "\n".join(files)
            conn.send(response.encode(FORMAT))


        elif cmd == "UPLOAD" and len(data) > 0:
            filename = data[1]
            filepath = os.path.join(SERVER_PATH, filename)
            conn.send("OK@Ready to recieve the file.".encode(FORMAT))

            with open(filepath, "wb") as f:
                while True:
                    bytes_read = conn.recv(SIZE)
                    if bytes_read == b"DONE":
                        break
                    f.write(bytes_read)
                conn.send("OK@File upload successful.".encode(FORMAT))

        elif cmd == "DOWNLOAD" and len(data) > 1:
            filename = data[1]
            filepath = os.path.join(SERVER_PATH, filename)

            if os.path.exists(filepath):
                conn.send("OK@Starting file transfer.".encode(FORMAT))

                with open(filepath, "rb") as f:
                    while bytes_read := f.read(SIZE):
                        conn.send(bytes_read)
                    conn.send(b"DONE")
            else:
                conn.send("ERROR@File not found.".encode(FORMAT))

        elif cmd == "DELETE":
            filename = data[0]
            filepath = os.path.join(SERVER_PATH, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                conn.send("OK@File deleted successfully.".encode(FORMAT))
            else:
                conn.send("ERROR@File not found.".encode(FORMAT))

    conn.close()
    print(f"User: {addr} has disconnected")

def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) ## used IPV4 and TCP connection
    server.bind(ADDR) # bind the address
    server.listen() ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept() ### accept a connection from a client
        thread = threading.Thread(target = handle_client, args = (conn, addr)) ## assigning a thread for each client
        thread.start()

if __name__ == "__main__":
    main()