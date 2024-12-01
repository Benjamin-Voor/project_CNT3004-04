# TODO: import time, and use it to calculate metrics like upload/download time and transfer rate.
    # The project requires collecting and analyzing performance metrics.
# TODO: cmd "DOWNLOAD"
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
    os.makedirs(CLIENT_DATA) # Make client_data folder if it doesn't exist

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR) # This could also use a try-except block...

    access_granted: bool = False

    while True:


        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        typo: bool = False

        if cmd == "UNAUTHENTICATED":
            access_granted = False
            print(f"{msg}")
        if cmd == "OK":
            access_granted = True
            print(f"{msg}") # By placing this at the top, 99% of commands will be addressed first

        # Benjamin believes the block below is a typo:
        elif cmd == "DISCONNECT" and not typo:
            print(f"msg")
            break
        # Idiot Developer types it differently at timestamp 18:04
        # Hyperlink: https://youtu.be/FQ-scCeKWas?si=Z7_QU1ZmvUJCsbPN
        elif cmd == "DISCONNECTED" and typo:
            print(f"[SERVER]: {msg}")
            break


        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        # This is the only command that does not require access_granted
        if cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break

        # authentication
        elif not access_granted:
            client.send(cmd.encode(FORMAT))  # send password attempt

        elif cmd == "HELP":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))

        elif cmd == "UPLOAD":
            path = data[1]
            filename = path.split("/")[-1]
            if os.path.exists(path):
                with open(path, "rb") as f:
                    file_data = f.read()
                if not typo:
                    send_data = f"{cmd}@{filename}@{len(file_data)}"
                else:
                    send_data = f"{cmd}@{filename}@{file_data}"
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

        elif cmd == "DOWNLOAD":
            print("Nope, that\'s not implemented yet!")
            continue

        elif cmd == "MKDIR":
            print("Nope, that\'s not implemented yet!")
            continue

        else:
            print(f"[client.py]: Unknown command: {cmd}")
            cmd = "LOGOUT"
            client.send(cmd.encode(FORMAT))
            break
            # otherwise it just gets stuck on an infinite loop.
            # Covering this edge case is not a requirement.
            # This is not important to deal with right now.
            # But at least now I won't have to restart the terminal every five seconds

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()