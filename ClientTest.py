import os
import socket

IP = "10.221.83.59"
PORT = 4450
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
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))



    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()