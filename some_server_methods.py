import hashlib
import logging
import os


SIZE = 65536
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

# Source: Geeks for Geeks. https://www.geeksforgeeks.org/sha-in-python/.
USERNAME = "username with spaces"
PASSWORD = "password with spaces"


logger = logging.getLogger('my logger')
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


def authentication(conn):
    # Source: Geeks for Geeks. https://www.geeksforgeeks.org/sha-in-python/.
    # Note: USERNAME and PASSWORD are globally-defined near the top of this file.

    ### username
    conn.send("UNAUTHENTICATED@Enter username (including spaces)".encode(FORMAT))
    received_username: bool = False
    access_granted: bool = False
    hash_username = hashlib.new('sha256', USERNAME.encode(FORMAT)).hexdigest()  # encryption
    while not received_username and not access_granted:
        try:
            cmd = conn.recv(SIZE).decode(FORMAT)
            if not cmd:
                continue  # Don't check if-statements until data is received.
        except ConnectionResetError:
            break
        if cmd == hash_username:
            received_username = True
            logging.info("Correct username entered (including spaces)")
            conn.send("UNAUTHENTICATED@Enter password".encode(FORMAT))
            break  # go to entering password
        elif cmd == "LOGOUT":
            break  # disconnect
        else:
            conn.send("UNAUTHENTICATED@Wrong username. Access denied!".encode(FORMAT))

    ### password
    hash_password = hashlib.new('sha256', PASSWORD.encode(FORMAT)).hexdigest()  # encryption
    while not access_granted and received_username:
        try:
            cmd = conn.recv(SIZE).decode(FORMAT)
            if not cmd:
                continue  # Don't check if-statements until data is received.
        except ConnectionResetError:
            break
        if cmd == hash_password:  # cmd is already hashed.
            logging.info("Correct password entered (including spaces)")
            conn.send("OK@Welcome to the File Server.".encode(FORMAT))
            access_granted = True
            break
        elif cmd == "LOGOUT":
            break
        else:
            conn.send(f"UNAUTHENTICATED@Wrong password. Access denied!".encode(FORMAT))
    return access_granted, received_username


def rmdir(cmd, conn, data):
    send_data = "OK@"
    name: str = ""
    try:
        if len(data) >= 2:
            name = data[1]
            filepath = os.path.join(SERVER_DATA_PATH, name)
            logging.debug(f"Attempting to remove directory: {filepath}")
            # Ensure the directory exists
            if not os.path.exists(filepath):
                logging.debug(f"Directory not found: {filepath}")
                send_data = f"ERROR@Directory \"{name}\" does not exist."
            # Ensure the directory is empty
            if os.listdir(filepath):
                send_data = f"ERROR@Directory \"{name}\" is not empty."
            os.rmdir(filepath)
            logging.info(f"Removed directory \"{name}\"")
            send_data += f"Directory \"{name}\" has been successfully removed!"
        else:
            send_data = "ERROR@No directory name provided"
    except IndexError as e:
        send_data = f"ERROR@Invalid input for \"{cmd}\" command. {e}"
    except OSError as e:
        send_data += f"Directory \"{name}\" cannot be removed. {e}"
    finally:
        conn.send(send_data.encode(FORMAT))


def mkdir(conn, data):
    if len(data) >= 2:
        dir_name = data[1]
        dir_path = os.path.join(SERVER_DATA_PATH, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info("Added directory \"{name}\"")
            send_data = f"OK@Directory '{dir_name}' created successfully."
        else:
            send_data = f"ERROR@Directory {dir_name} already exists."
        conn.send(send_data.encode(FORMAT))
    else:
        send_data = "ERROR@Invalid directory name."
        conn.send(send_data.encode(FORMAT))
