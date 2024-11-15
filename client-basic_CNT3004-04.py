#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author : Ayesha S. Dina

import os
import socket

IP = "localhost"
PORT = 4450
ADDR = (IP,PORT)
SIZE = 1024 ## byte .. buffer size
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

def main():
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDR)
    while True:  ### multiple communications
        data = client.recv(SIZE).decode(FORMAT)
        cmd, msg = data.split("@")
        if cmd == "OK":
            print(f"{msg}")
        elif cmd == "DISCONNECTED":
            print(f"{msg}")
            break
        
        data = input("> ") 
        data = data.split(" ")
        cmd = data[0]

        if cmd == "TASK":
            client.send(cmd.encode(FORMAT))

        elif cmd == "HELP":
            client.send(cmd.encode(FORMAT)) # Source is from Dina: https://github.com/ayeshasdina/SOCKET-PROGRAMMING-with-Python/blob/main/client_2.py

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            break



    print("Disconnected from the server.")
    client.close() ## close the connection

if __name__ == "__main__":
    main()