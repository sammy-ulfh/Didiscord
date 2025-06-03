#!/usr/bin/env python3

from server import Server
import socket

def main():
    HOST = '127.0.0.1' #socket.gethostbyname(socket.gethostname())
    PORT = input("\n[+] Ingrese el puerto: ")

    while True:
        try:
            PORT = int(PORT)
            break
        except:
            continue

    server = Server(HOST, PORT)

if __name__ == '__main__':
    main()
