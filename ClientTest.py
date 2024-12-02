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
FORMAT = "utf-8"
SIZE = 1024
CLIENT_DATA_PATH = "client_data"

if not os.path.exists(CLIENT_DATA_PATH):
    os.makedirs(CLIENT_DATA_PATH) # Ensure client_data folder exists
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
    try:
        client.connect(ADDR)
    except ConnectionRefusedError as e:
        logging.error("Connection failed.")
        raise ConnectionRefusedError("Refactor \"IP\" variable to Server\'s IP. Also, Start ServerTest.py on server machine before starting ClientTest.py.\n")

    access_granted: bool = False # authentication
    typo: bool = True # Drew and Benjamin disagree on whether code should run one way or the other. When we finally agree, we'll flick this to true or false, or find and delete the unwanted blocks of code.

    while True:

        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        if "@" in data:
            cmd, msg = data.split("@", 1)
        else:
            cmd, msg = data, ""

        if cmd == "UNAUTHENTICATED":
            access_granted = False
            print(f"{msg}")
        elif cmd == "OK":
            access_granted = True
            print(f"{msg}")
        elif cmd == "ERROR":
            logging.error(f"{msg}")

        elif cmd == "DISCONNECTED":
            print(f"[SERVER]: {msg}")
            break

        else:
            print(f"{msg}")

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        # This is the only command that does not require access_granted
        if cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break

        elif cmd == "LIST_SERVER":

        # authentication
        elif not access_granted:
            password_attempt = hashlib.sha256(cmd.encode(FORMAT)).hexdigest() # encrypt before sending
            client.send(password_attempt.encode(FORMAT))  # send password attempt

        elif cmd == "HELP":
            client.send(cmd.encode(FORMAT))


        elif cmd == "UPLOAD":
        try:
            path = data[1]
            filename = os.path.basename(path)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    file_data = f.read()

                send_data = f"{cmd}@{filename}@{len(file_data)}"
                client.send(send_data.encode(FORMAT))

                for i in range(0, len(file_data), SIZE):
                    client.send(file_data[i:i + SIZE])

                print(f"File {filename} has been sent successfully.")
            else:
                print(f"Error: Requested file {path} does not exist.")
        except Exception as e:
            print(f"An error occurred during file upload: {e}")



        elif cmd == "DOWNLOAD":
        try:
            filename = data[1]
            client.send(f"{cmd}@{filename}".encode(FORMAT))

            response = client.recv(SIZE).decode(FORMAT)
            print(f"Response from server: {response}")

            if "@" in response:
                response_cmd, response_msg = response.split("@", 1)
                if response_cmd == "OK":
                    file_size = int(response_msg)
                    file_path = os.path.join(CLIENT_DATA_PATH, filename)

                    with open(file_path, "wb") as f:
                        bytes_received = 0
                        while bytes_received < file_size:
                            chunk = client.recv(SIZE)
                            if not chunk:
                                print("No more data received.")
                                break
                            f.write(chunk)
                            bytes_received += len(chunk)
                            print(f"Bytes received: {bytes_received}")

                    print(f"File {filename} has been downloaded successfully.")
                    continue
                else:
                    print(f"Error: {response_msg}")
                    continue
            else:
                print(f"Unexpected server response: {response}")
            # Ensure the loop continues after handling the response
            continue
        except Exception as e:
            print(f"An error occurred during file download: {e}")
            continue

        elif cmd == "DELETE":
            try:
                path = data[1]
            except IndexError as e:
                raise IndexError("Invalid input for DELETE command. Enter \"HELP\" for correct implementation.") from e
                # invalid_message(cmd)
                # continue
            client.send(f"{cmd}@{path}".encode(FORMAT))

        elif cmd == "MKDIR":
            if len(data) == 2:
                dir_name = data[1]
                client.send(f"{cmd}@{dir_name}".encode(FORMAT))
            else:
            client.send(cmd.encode(FORMAT))

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
            logging.error(f"[client.py]: Unknown command: {cmd}")

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()
