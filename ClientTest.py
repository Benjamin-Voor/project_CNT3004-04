# TODO: import time, and use it to calculate metrics like upload/download time and transfer rate.
    # The project requires collecting and analyzing performance metrics.
# TODO: cmd "DOWNLOAD"
# TODO: username/password authentication
# TODO: support pics & vids
# TODO: cmd mkdir
# TODO: cmd ls

import os
import socket

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4450 # Make sure the port matches with the server
ADDR = (IP, PORT)
SIZE = 1024  ## byte .. buffer size
FORMAT = "utf-8"
CLIENT_DATA = "client_data"

if not os.path.exists(CLIENT_DATA):
    os.makedirs(CLIENT_DATA)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:

        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "OK":
            print(f"{msg}")

        elif cmd == "DISCONNECT":
            print(f"msg")
            break

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break

        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))

        elif cmd == "UPLOAD":
            path = data[1]
            filename = path.split("/")[-1]
            if os.path.exists(path):
                with open(path, "rb") as f:
                    file_data = f.read()
                send_data = f"{cmd}@{filename}@{len(file_data)}"
                client.send(send_data.encode(FORMAT))
                chunk_size = 1024
                for i in range(0, len(file_data), chunk_size):
                    client.send(file_data[i:i+chunk_size])


                print(f"File {filename} has been sent successfully.")
            else:
                print(f"Error: Requested file does not exist.")


        elif cmd == "DELETE":
            try:
                client.send(f"{cmd}@{data[1]}".encode(FORMAT))
            except IndexError as e:
                raise IndexError("Invalid input for DELETE command. Enter \"HELP\" for correct implementation.") from e


    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()