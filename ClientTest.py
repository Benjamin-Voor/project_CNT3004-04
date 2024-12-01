# TODO: import time, and use it to calculate metrics like upload/download time and transfer rate.
    # The project requires collecting and analyzing performance metrics.
# TODO: cmd "DOWNLOAD"
# TODO: cmd mkdir
# TODO: cmd ls

import os
import socket
import hashlib
import logging

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
# Equivalent to `os.makedirs(CLIENT_DATA, exist_ok=True)`

logger = logging.getLogger('my logger')
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

def invalid_message(cmd):
    invalid_msg = f"Invalid input for {cmd} command. Enter \"HELP\" for correct implementation."
    print(invalid_msg)


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # AF_INET = IPv4
        # SOCK_STREAM = TCP
    client.connect(ADDR) # This could also use a try-except block...
    access_granted: bool = False # authentication
    typo: bool = False # Drew and Benjamin disagree on whether code should run one way or the other. When we finally agree, we'll flick this to true or false, or find and delete the unwanted blocks of code.

    while True:


        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")

        if cmd == "UNAUTHENTICATED":
            access_granted = False
            print(f"{msg}")
        if cmd == "OK":
            access_granted = True
            print(f"{msg}")

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
            password_attempt = hashlib.sha256(cmd.encode(FORMAT)).hexdigest() # encrypt before sending
            client.send(password_attempt.encode(FORMAT))  # send password attempt

        elif cmd == "HELP":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))

        elif cmd == "UPLOAD":
            try:
                path = data[1]
            except IndexError as e:
                raise IndexError("Invalid input for DELETE command. Enter \"HELP\" for correct implementation.") from e

            filename = path.split("/")[-1]
            if os.path.exists(path):
                logging.info("Valid command. Writing file...")
                with open(path, "rb") as f:
                    file_data = f.read()

                # Benjamin believes the block below is a typo:
                if not typo:
                    send_data = f"{cmd}@{filename}@{len(file_data)}"
                else:
                    send_data = f"{cmd}@{filename}@{file_data}"
                # If Drew opens and reads the uploaded text file, he'd see the contents are the length of the data, not the data itself
                    # Unless he types it MY way (I'm Benjamin)

                client.send(send_data.encode(FORMAT))
                if not typo:
                    chunk_size = 1024 # chunk_size is equivalent to global constant SIZE. Why re-define here?
                    for i in range(0, len(file_data), chunk_size):
                        client.send(file_data[i:i+chunk_size])
                else:
                    for i in range(0, len(file_data), SIZE):
                        client.send(file_data[i:i+SIZE])

                print(f"File {filename} has been sent successfully.")
            else:
                print(f"Error: Requested file does not exist.")


        elif cmd == "DELETE":
            try:
                path = data[1]
            except IndexError as e:
                raise IndexError("Invalid input for DELETE command. Enter \"HELP\" for correct implementation.") from e
                # invalid_message(cmd)
                # continue
            client.send(f"{cmd}@{path}".encode(FORMAT))

        elif cmd == "DOWNLOAD":
            print("Nope, that\'s not implemented yet!")
            continue

        elif cmd == "MKDIR":
            try:
                path = data[1]
            except IndexError as e:
                raise IndexError(f"Invalid input for {cmd} command. Enter \"HELP\" for correct implementation.") from e
                # invalid_message(cmd)
                # continue

            filename = path.split("/")[-1]
            send_data = f"{cmd}@{path}"
            client.send(send_data.encode(FORMAT))

        elif cmd == "RMDIR":
            try:
                path = data[1]
            except IndexError as e:
                raise IndexError(f"Invalid input for {cmd} command. Enter \"HELP\" for correct implementation.") from e
                # invalid_message(cmd)
                # continue

            filename = path.split("/")[-1]
            send_data = f"{cmd}@{path}"
            client.send(send_data.encode(FORMAT))

        else:
            print(f"[client.py]: Unknown command: {cmd}")

            # Drew has " resolved the aforementioned infinite looping, it now allows you to make infinite mistakes when trying to type in commands. so if you screw up a command you can enter it and it will actually execute."
            # Until he uploads his code, this code will break you out.

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