import os
import socket

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
    os.makedirs(CLIENT_DATA_PATH)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print("Connected to the server")

    while True:

        ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        if "@" in data:
            cmd, msg = data.split("@", 1)
        else:
            cmd, msg = data, ""

        print(f"{msg}")

        data = input("> ")
        data = data.split(" ")
        cmd = data[0]

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))
        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break
        elif cmd == "LIST_SERVER":
            client.send(cmd.encode(FORMAT))
        elif cmd == "DELETE":
            client.send(f"{cmd}@{data[1]}".encode(FORMAT))
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

        elif cmd == "MAKEDIR":
            if len(data) == 2:
                dir_name = data[1]
                client.send(f"{cmd}@{dir_name}".encode(FORMAT))
        else:
            client.send(cmd.encode(FORMAT))

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()
