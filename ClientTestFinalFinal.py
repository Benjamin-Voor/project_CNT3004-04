import os
import socket
import hashlib
import logging

from ServerTestFinal import authentication

IP = "localhost"
    ### Make sure this number matches the server you're connecting to.
    # If both server and client are the same machine, then use these commands:
        # "localhost" # socket.gethostbyname(socket.gethostname())
PORT = 4451 # Make sure the port matches with the server
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
CLIENT_DATA_PATH = "client_data"

if not os.path.exists(CLIENT_DATA_PATH):
    os.makedirs(CLIENT_DATA_PATH) # Ensure client_data folder exists
# Equivalent to `os.makedirs(CLIENT_DATA, exist_ok=True)`

def prRed(skk): print("\033[91m {}\033[00m" .format(skk)) # Source: Geeks For Geeks. https://www.geeksforgeeks.org/print-colors-python-terminal/

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
        client.connect(ADDR) # ¿Why does this line raise an OSError?
    except ConnectionRefusedError:
        logging.error("Connection failed.")
        raise ConnectionRefusedError("Refactor \"IP\" variable to Server\'s IP. Also, Start Server on server machine before starting Client on client machine.\n")

    access_granted: bool = False # authentication

    while True:

        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        if "@" in data:
            cmd, msg = data.split("@", 1)
        else:
            cmd, msg = data, ""
        match cmd:
            case "UNAUTHENTICATED":
                access_granted = False
                print(f"{msg}")
            case "OK":
                access_granted = True
                print(f"{msg}")
            case "ERROR":
                prRed(f"{msg}")
            case "DISCONNECTED":
                print(f"[SERVER]: {msg}")
                break
            case _:
                print(f"{msg}")



        if not access_granted:
            # This is the only command that does not require access_granted
            if cmd == "LOGOUT":
                client.send(cmd.encode(FORMAT))
                break


            authentication_attempt = input("> ") # supports spaces
            authentication_attempt_hashed = hashlib.sha256(authentication_attempt.encode(FORMAT)).hexdigest() # encrypt before sending
            client.send(authentication_attempt_hashed.encode(FORMAT))  # send authentication attempt
            continue

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        match cmd:
            case "LIST_SERVER":
                client.send(cmd.encode(FORMAT))


            case "HELP":
                client.send(cmd.encode(FORMAT))


            case "UPLOAD":
                if len(data) >= 2:
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
                        prRed(f"Error: Requested file {path} does not exist.")
                        cmd = "ERROR"
                        client.send(cmd.encode(FORMAT))
                else:
                    prRed(f"Error: No directory name provided")
                    cmd = "ERROR"
                    client.send(cmd.encode(FORMAT))



            case "DOWNLOAD":
                try:
                    filename = data[1]
                    client.send(f"{cmd}@{filename}".encode(FORMAT))

                    response = client.recv(SIZE).decode(FORMAT)
                    # rRed(f"Response from server: {response}") # Not user-friendly to see

                    if "@" in response:
                        response_cmd, response_msg = response.split("@", 1)
                        if response_cmd == "OK":
                            file_size = int(response_msg)
                            print(f"File exists. Size is {response_msg} bytes") # more user friendly
                            file_path = os.path.join(CLIENT_DATA_PATH, filename)

                            with open(file_path, "wb") as f:
                                bytes_received = 0
                                while bytes_received < file_size:
                                    chunk = client.recv(SIZE)
                                    if not chunk:
                                        #print("No more data received.")
                                        break
                                    f.write(chunk)
                                    bytes_received += len(chunk)
                                    #print(f"Bytes received: {bytes_received}")

                            print(f"File {filename} has been downloaded successfully.")
                            continue
                        else:
                            prRed(f"Error: {response_msg}")
                            cmd = "ERROR"  # This line only makes sense on Client side.
                            client.send(cmd.encode(FORMAT))
                            continue
                    else:
                        prRed(f"Unexpected server response: {response}")
                        cmd = "ERROR"  # This line only makes sense on Client side.
                        client.send(cmd.encode(FORMAT))
                    # Ensure the loop continues after handling the response
                    continue
                except Exception as e:
                    prRed(f"An error occurred during file download: {e}")
                    cmd = "ERROR"  # This line only makes sense on Client side.
                    client.send(cmd.encode(FORMAT))


            case "DELETE":
                if len(data) == 2:
                    path = data[1]
                    client.send(f"{cmd}@{path}".encode(FORMAT))
                else:
                    client.send(cmd.encode(FORMAT))


            case "MKDIR":
                if len(data) == 2:
                    dir_name = data[1]
                    client.send(f"{cmd}@{dir_name}".encode(FORMAT))
                else:
                    client.send(cmd.encode(FORMAT))


            case "RMDIR":
                if len(data) == 2:
                    dir_name = data[1]
                    file_path = dir_name.split("/")[-1]
                    send_data = f"{cmd}@{file_path}"
                    client.send(send_data.encode(FORMAT))
                else:
                    client.send(cmd.encode(FORMAT))


            case _:
                client.send(cmd.encode(FORMAT))

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()
