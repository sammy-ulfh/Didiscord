#!/usr/bin/env python3

import threading
import socket
import time
import ssl

class Server:

    def __init__(self, HOST, MSG_PORT):
        self.HOST = HOST
        self.MSG_PORT = MSG_PORT
        self.USERS_PORT = MSG_PORT + 1
        self.FILES_PORT = MSG_PORT + 2
        self.IMAGES_PORT = MSG_PORT + 3
        self.VOICE_PORT = MSG_PORT + 4
        self.VOICES_PORT = MSG_PORT + 5
        self.msg_clients = []
        self.file_clients = []
        self.image_clients = []
        self.voice_clients = []
        self.voice_usernames = {}
        self.usernames = {}
        self.images = []
        self.files = []
        self.sending_image = False

        self.server()

    def send_audio(self, client, data):
        try:
            client.sendall(data)
        except:
            pass

    def voice_connection(self, client_socket):

        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024)

                    if not data:
                        break

                    try:
                        data = data.decode()
                        if data == "OUT":
                            break
                    except:
                        pass

                    for client in self.voice_clients:
                        if client is not client_socket:
                            thread = threading.Thread(target=self.send_audio, args=(client, data))
                            thread.daemon = True
                            thread.start()
                except:
                    break

        self.voice_clients.remove(client_socket)
        del self.voice_usernames[client_socket]

    def client_voice(self, client_socket):

        while True:
            try:
                client, addr = client_socket.accept()

                self.voice_clients.append(client)
                self.voice_usernames[client] = client.recv(1024).decode()

                thread = threading.Thread(target=self.voice_connection, args=(client,))
                thread.daemon = True
                thread.start()
            except:
                break

    def send_files(self):

        while True:

            if self.files:

                file = self.files[0]
                del self.files[0]

                index = 0

                while index < len(file):
                    if index == 0:
                        socket = file[0]
                    else:
                        time.sleep(0.1)
                        for client in self.file_clients:
                            if client is not socket:
                                client.sendall(file[index])
                    index += 1
            else:
                time.sleep(5)

    def send_images(self):

        while True:

            if self.images:

                img = self.images[0]
                del self.images[0]

                index = 0

                while index < len(img):
                    if index == 0:
                        socket = img[0]
                    else:
                        time.sleep(0.1)
                        for client in self.image_clients:
                            if client is not socket:
                                client.sendall(img[index])
                    index += 1
            else:
                time.sleep(5)


    def client_images(self, client_images):

        with client_images as client_image:

            self.image_clients.append(client_image)

            while True:
                try:
                    file = client_image.recv(8000)


                    if not file:
                        break

                    img = []
                    img.append(client_image)
                    img.append(file)

                    data = True
                    while data:
                        data = client_image.recv(8000)
                        img.append(data)

                        try:
                            if data.decode() == "END":
                                break
                            if data.decode() == "FIN":
                                self.images.append(img)
                                break
                        except:
                            continue
                except:
                    break

            self.image_clients.remove(client_image)


    def client_files(self, files_client):

        with files_client as client_file:

            self.file_clients.append(client_file)

            while True:
                try:
                    name = client_file.recv(8000)


                    if not name:
                        break

                    file = []
                    file.append(client_file)
                    file.append(name)

                    data = True
                    while data:
                        data = client_file.recv(8000)
                        file.append(data)

                        try:
                            if data.decode() == "END":
                                break
                            if data.decode() == "FIN":
                                self.files.append(file)
                                break
                        except:
                            continue
                except:
                    break

            self.file_clients.remove(client_file)

    def client_users(self, usr_client): 

        with usr_client as client:

            while True:
                try:
                    client.sendall(', '.join(self.usernames.values()).encode())
                    time.sleep(10)
                except:
                    break

    def client_voices(self, client_socket):

        with client_socket as client:

            while True:
                try:
                    if self.voice_usernames:
                        client.sendall(', '.join(self.voice_usernames.values()).encode())
                    else:
                        client.sendall('NULL'.encode())
                    time.sleep(1)
                except:
                    break

    def client_msg(self, msg_client):

        with msg_client as msg_client:

            username = msg_client.recv(1024).decode()

            self.usernames[msg_client] = username
            self.msg_clients.append(msg_client)

            for client in self.msg_clients:
                if client is not msg_client:
                    client.sendall(f"\n[+] El usuario {username} se ha unido al chat.\n".encode())

            while True:
                try:
                    message = msg_client.recv(8000)

                    if not message:
                        break

                    for client in self.msg_clients:
                        if client is not msg_client:
                            client.sendall(message)
                except:
                    break

            try:
                msg_client.sendall("CLOSE".encode())
            except:
                pass

            for client in self.msg_clients:
                if client is not msg_client:
                    client.sendall(f"\n[+] El usuario {username} ha abandonado el chat.\n".encode())
            self.msg_clients.remove(msg_client)
            del self.usernames[msg_client]

    def server(self):


        msg = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        usrs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        files = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        images = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        voice_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        voices = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        msg.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        msg.bind((self.HOST, self.MSG_PORT))
        msg.listen()

        usrs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        usrs.bind((self.HOST, self.USERS_PORT))
        usrs.listen()

        files.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        files.bind((self.HOST, self.FILES_PORT))
        files.listen()

        images.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        images.bind((self.HOST, self.IMAGES_PORT))
        images.listen()

        voice_chat.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        voice_chat.bind((self.HOST, self.VOICE_PORT))
        #voice_chat = self.context.wrap_socket(voice_chat, keyfile="server-key.key", certfile="server-cert.pem", server_side=True)
        voice_chat.listen()

        print(f"\n[+] Servidor en escucha en: {self.HOST}:{self.MSG_PORT}\n")

        voices.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        voices.bind((self.HOST, self.VOICES_PORT))
        voices.listen()

        thread_voice = threading.Thread(target=self.client_voice, args=(voice_chat,))
        thread_voice.daemon = True
        thread_voice.start()

        thread_img = threading.Thread(target=self.send_images)
        thread_img.daemon = True
        thread_img.start()

        thread_file = threading.Thread(target=self.send_files)
        thread_file.daemon = True
        thread_file.start()

        while True:

            msg_client, addr = msg.accept()

            thread1 = threading.Thread(target=self.client_msg, args=(msg_client,))
            thread1.daemon = True
            thread1.start()

            usrs_client, addr = usrs.accept()

            thread2 = threading.Thread(target=self.client_users, args=(usrs_client,))
            thread2.daemon = True
            thread2.start()

            files_client, addr = files.accept()

            thread3 = threading.Thread(target=self.client_files, args=(files_client,))
            thread3.daemon = True
            thread3.start()

            images_client, addr = images.accept()

            thread4 = threading.Thread(target=self.client_images, args=(images_client,))
            thread4.daemon = True
            thread4.start()

            voices_client, addr = voices.accept()

            thread5 = threading.Thread(target=self.client_voices, args=(voices_client,))
            thread5.daemon = True
            thread5.start()

    @property
    def context(self):
        """The context property."""
        return self.__context

    @context.setter
    def context(self, value):
        self.__context = value
