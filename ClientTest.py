import os
import socket
import time

IP = "10.221.82.245"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024  ## byte .. buffer size
FORMAT = "utf-8"
CLIENT_DATA = "client_data"

if not os.path.exists(CLIENT_DATA):
    os.makedirs(CLIENT_DATA)



def list_local_files():
    ###List files in the client's local directory.
    files = os.listdir(CLIENT_DATA)
    if files:
        print("Files in client directory:")
        for filename in files:
            print(f" - {filename}")
    else:
        print("No files in client directory.")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    ### multiple communications
    data = client.recv(SIZE).decode(FORMAT)
    msg = data.split("@")


    while True:
        command = input("> ")
        client.send(command.encode(FORMAT))
        cmd, *data = command.split(" ")

        if cmd == "LIST":
            response = client.recv(SIZE).decode(FORMAT)
            print(response.split("@")[1])

        elif cmd == "UPLOAD" and len(data) > 0:
            filename = data[0]
            upload_file(client, filename)


        elif cmd == "DOWNLOAD" and len(data) > 0:
            filename = data[0]
            download_file(client, filename)


        elif cmd == "DELETE":
            response = client.recv(SIZE).decode(FORMAT)
            print(response.split("@")[1])

        elif cmd == "OK":
            print(f"{msg}")

        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break

        elif cmd == "TASK":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break


    print("Disconnected from the server.")
    client.close()  ## close the connection

def upload_file(client, filename):
    filepath = os.path.join(CLIENT_DATA, filename)

    if os.path.exists(filepath):
        client.recv(SIZE)

        total_bytes_sent = 0
        start_time = time.time()

        with open(filepath, "rb") as f:
            while bytes_read := f.read(SIZE):
                client.send(bytes_read)
                total_bytes_sent += len(bytes_read)
        client.send(b"DONE")

        duration, transfer_rate = calculate_metrics(total_bytes_sent, start_time)

        print(f"Uploaded {filename} successfully!")
        print(f"Total bytes sent: {total_bytes_sent} bytes")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Average Transfer Rate: {transfer_rate:.2f} KB/s")

        print(client.recv(SIZE).decode(FORMAT))
    else:
        print("File does not exist.")

def download_file(client, filename):
    filepath = os.path.join(CLIENT_DATA, filename)

    response = client.recv(SIZE).decode(FORMAT)
    if "OK@" in response:

        total_bytes_received = 0
        start_time = time.time()

        with open(filepath, "wb") as f:
            while True:
                bytes_read = client.recv(SIZE)
                if bytes_read == b"DONE":
                    break
                f.write(bytes_read)
                total_bytes_received += len(bytes_read)

        duration, transfer_rate = calculate_metrics(total_bytes_received, start_time)

        print(f"Downloaded {filename} successfully!")
        print(f"Total bytes sent: {total_bytes_received} bytes")
        print(f"Time taken: {duration:.2f} seconds")
        print(f"Average Transfer Rate: {transfer_rate:.2f} KB/s")
        print(f"Downloaded {filename}")
    else:
        print("File not found on server.")

def calculate_metrics(total_bytes, start_time):
    end_time = time.time()
    duration = end_time - start_time
    transfer_rate = (total_bytes / 1024) / duration  # KB per second
    return duration, transfer_rate

if __name__ == "__main__":
    main()