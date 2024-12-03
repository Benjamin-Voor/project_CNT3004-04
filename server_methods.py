import hashlib


def authentication(conn, format="utf-8", username="username with spaces", password="password with spaces"):
    # Source: Geeks for Geeks. https://www.geeksforgeeks.org/sha-in-python/.
    # Note: USERNAME and PASSWORD are globally-defined near the top of this file.

    ### username
    conn.send("UNAUTHENTICATED@Enter username (including spaces)".encode(format))
    received_username: bool = False
    access_granted: bool = False
    hash_username = hashlib.new('sha256', username.encode(format)).hexdigest()  # encryption
    while not received_username and not access_granted:
        try:
            cmd = conn.recv(SIZE).decode(format)
            if not cmd:
                continue  # Don't check if-statements until data is received.
        except ConnectionResetError:
            break
        if cmd == hash_username:
            received_username = True
            logging.info("Correct username entered (including spaces)")
            conn.send("UNAUTHENTICATED@Enter password".encode(format))
            break  # go to entering password
        elif cmd == "LOGOUT":
            break  # disconnect
        else:
            conn.send("UNAUTHENTICATED@Wrong username. Access denied!".encode(format))

    cmd = ""  # Do not input username to password function

    ### password
    hash_password = hashlib.new('sha256', password.encode(format)).hexdigest()  # encryption
    while not access_granted and received_username:
        try:
            cmd = conn.recv(SIZE).decode(format)
            if not cmd:
                continue  # Don't check if-statements until data is received.
        except ConnectionResetError:
            break
        if cmd == hash_password:  # cmd is already hashed.
            logging.info("Correct password entered (including spaces)")
            conn.send("OK@Welcome to the File Server.".encode(format))
            access_granted = True
            break
        elif cmd == "LOGOUT":
            break
        else:
            conn.send(f"UNAUTHENTICATED@Wrong password. Access denied!".encode(format))
    return access_granted, received_username
