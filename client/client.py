import socket
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog, messagebox

from PIL import Image
import io
import os
import time
import threading
import pygame
import pyaudio
import ssl

class Client:

    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.USERS_PORT = PORT + 1
        self.FILES_PORT = PORT + 2
        self.IMAGES_PORT = PORT + 3
        self.VOICE_PORT = PORT + 4
        self.VOICES_PORT = PORT + 5
        self.username = ''
        self.default_path = ''
        self.users = []
        self.users_voice = []
        self.FrameLeft = None
        self.FrameCenter = None
        self.FrameRight = None

        self.sending_image = False
        self.sending_file = False

        self.audio = pyaudio.PyAudio()
        self.speaking = True
        self.listening = True
        self.voice_users_cont = 0
        self.voice_users_cont_last = 0

        self.active_listening = False


    def out_call(self, button_out, voice_socket):

        with voice_socket:
            voice_socket.sendall("OUT".encode())
            self.active_listening = False
            button_out.destroy()

            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/leave_call.mp3')
            pygame.mixer.music.play()

    def current_voice(self, voice_socket):

        with voice_socket:
            stream_input = self.audio.open(format=pyaudio.paInt16, channels=2, rate=44100, input=True, frames_per_buffer=1024)
            while True:
                try:
                    if self.speaking and self.active_listening:
                        data = stream_input.read(1024)
                        voice_socket.sendall(data)
                        time.sleep(0.001)
                    elif not self.active_listening:
                        break
                    else:
                        data = stream_input.read(1024)
                        time.sleep(0.001)
                except:
                    break
            stream_input.close()

    def recv_voice(self, voice_socket):

        with voice_socket:
            stream_output = self.audio.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True, frames_per_buffer=1024)

            while True:
                try:
                    if self.active_listening and self.listening:
                        data = voice_socket.recv(1024)
                        stream_output.write(data)
                        time.sleep(0.001)
                    elif not self.active_listening:
                        break
                    else:
                        data = voice_socket.recv(1024)
                        time.sleep(0.001)
                except:
                    break
            stream_output.close()

    def active_voice(self, bottom_frame_icons):


        if not self.active_listening:

            try:
                voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #voice_socket = ssl.wrap_socket(voice_socket)
                voice_socket.connect((self.HOST, self.VOICE_PORT))
                voice_socket.sendall(self.username.encode())
            except:
                msg = CTkMessagebox(title="Error", message="Error al conectarse al chat de voz.", icon="warning", option_1="OK")
                msg.get()
                return

            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/join_call.mp3')
            pygame.mixer.music.play()
            self.active_listening = True

            icon_out = CTkImage(light_image=Image.open('./icon/phone-out.png'), dark_image=Image.open('./icon/phone-out.png'), size=(30, 30))
            button_out = CTkButton(bottom_frame_icons, text='', image=icon_out, fg_color='transparent', corner_radius=100, width=1)
            button_out.configure(command=lambda: self.out_call(button_out, voice_socket))
            button_out.pack(side=RIGHT, pady=(6, 0))

            thread = threading.Thread(target=self.current_voice, args=(voice_socket,))
            thread.daemon = True
            thread.start()

            thread_recv = threading.Thread(target=self.recv_voice, args=(voice_socket,))
            thread_recv.daemon = True
            thread_recv.start()

    def sound(self, button_sound, button_mic, icon_sound):

        if self.listening:

            self.listening = False
            self.speaking = False

            icon_sound_mute = CTkImage(light_image=Image.open('./icon/sound-mute-light.png'), dark_image=Image.open('./icon/sound-mute-dark.png'), size=(25, 25))
            icon_mic_mute = CTkImage(light_image=Image.open('./icon/microfone-mute-light.png'), dark_image=Image.open('./icon/microphone-mute-dark.png'), size=(25, 25))

            button_sound.configure(image=icon_sound_mute)
            button_mic.configure(image=icon_mic_mute)

            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/deafen.mp3')
            pygame.mixer.music.play()
        else:

            self.listening = True
            button_sound.configure(image=icon_sound)

            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/undeafen.mp3')
            pygame.mixer.music.play()

    def mic(self, button, icon_mic, button_sound, icon_sound):

        if self.listening:
            if self.speaking:

                self.speaking = False

                icon_mute = CTkImage(light_image=Image.open('./icon/microfone-mute-light.png'), dark_image=Image.open('./icon/microphone-mute-dark.png'), size=(25, 25))
                button.configure(image=icon_mute)

                pygame.mixer.init()
                pygame.mixer.music.load('./sounds/mute.mp3')
                pygame.mixer.music.play()
            else:

                self.speaking = True
                button.configure(image=icon_mic)

                pygame.mixer.init()
                pygame.mixer.music.load('./sounds/unmute.mp3')
                pygame.mixer.music.play()
        else:
            self.listening = True
            self.speaking = True
            button.configure(image=icon_mic)
            button_sound.configure(image=icon_sound)

            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/unmute.mp3')
            pygame.mixer.music.play()

    def download_file(self, name, data):

            if not self.default_path:
                msg = CTkMessagebox(title="Selección de directorio", message="Seleccionará una carpeta donde se almacenarán los archivos e imágenes.", option_1="OK")
                if msg.get() == "OK":
                    if os.name == "posix":
                        path = filedialog.askdirectory(initialdir="/home", title="Selección de directorio")
                    else:
                        try:
                            path = filedialog.askdirectory(initialdir="/Users", title="Selección de directorio")
                        except:
                            path = filedialog.askdirectory(initialdir="/Usuarios", title="Selección de directorio")
                    self.default_path = path
                else:
                    return
            else:
                path = self.default_path

            if path:
                path += f"/{name}"
            else:
                return

            if path:

                try:
                    with open(path, 'w') as f:
                        f.write(data)
                except:
                    try:
                        with open(path, 'wb') as f:
                            f.write(data)
                    except:
                        msg = CTkMessagebox(title="Error", message="Error al descargar el archivo.", icon="warning", option_1="OK")
                        msg.get()

                msg = CTkMessagebox(title="Descarga", message=f"{name} almacenado correctamente en {self.default_path}", icon="check", option_1="OK")
                msg.get()

    def download_as(self, name, data):

        if os.name == "posix":
            path = filedialog.asksaveasfilename(initialdir="/home", initialfile=name ,title="Save file as")
        else:
            try:
                path = filedialog.asksaveasfilename(initialdir="/Users", initialfile=name, title="Save file as")
            except:
                path = filedialog.asksaveasfilename(initialdir="/Usuarios", initialfile=name, title="Save file as")

        if path:

            try:
                with open(path, 'w') as f:
                    f.write(data)
            except:
                try:
                    with open(path, 'wb') as f:
                        f.write(data)
                except:
                    msg = CTkMessagebox(title="Error", message="Error al descargar el archivo.", icon="warning", option_1="OK")
                    msg.get()
                    return

            msg = CTkMessagebox(title="Descarga", message=f"{path.split('/')[-1]} almacenado correctamente en {'/'.join([p for p in path.split('/') if not p == path.split('/')[-1]])}", option_1="OK")
            msg.get()

    def download_image(self, name, data):

        if not self.default_path:
            msg = CTkMessagebox(title="Selección de directorio", message="Seleccionará una carpeta donde se almacenarán los archivos e imágenes.", option_1="OK")
            if msg.get() == "OK":
                if os.name == "posix":
                    path = filedialog.askdirectory(initialdir="/home", title="Selección de directorio")
                else:
                    try:
                        path = filedialog.askdirectory(initialdir="/Users", title="Selección de directorio")
                    except:
                        path = filedialog.askdirectory(initialdir="/Usuarios", title="Selección de directorio")
                self.default_path = path
            else:
                return
        else:
            path = self.default_path

        if path:
            path += f"/{name}"
        else:
            return

        if path:

            try:
                if path[-4:len(path)] == ".png" or path[-4:len(path)] == ".jpg" or path[-5:len(path)] == ".jpeg":
                    with open(path, 'wb') as f:
                        f.write(data)
                else:
                    path += ".png"
                    with open(path, 'wb') as f:
                        f.write(data)
            except:
                msg = CTkMessagebox(title="Error", message="Error al descargar la imagen.", icon="warning", option_1="OK")
                msg.get()
                return

            msg = CTkMessagebox(title="Descarga", message=f"{name} almacenada correctamente en {self.default_path}", icon="check", option_1="OK")
            msg.get()

    def show_image(self, top_frame, side, name, data):

        max_width = 600

        img_byte = Image.open(io.BytesIO(data))
        width, height = img_byte.size

        while width > max_width:
            width /= 2
            height /=2

        while width < max_width:
            width *= 2
            height *= 2

            if width > max_width:
                width /= 2
                height /= 2
                break

        index = name.index(':')
        username = name[0:index]
        name = name[index+1:len(name)]

        img_tk = CTkImage(light_image=img_byte, dark_image=img_byte, size=(width, height))

        frame = CTkFrame(top_frame, fg_color="#000000", border_color="white", border_width=2)

        if side == "right":
            frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='ne')
        elif side == "left":
            frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='nw')

        label_username = CTkLabel(frame, text=username, font=('MathJax_Math', 18), wraplength=290, justify=LEFT, anchor='w')
        label_username.pack(padx=10, pady=(3, 0), fill=X, expand=True)

        label = CTkLabel(frame, image=img_tk, text="")
        label.pack(padx=3, fill=X, expand=True)

        download_button = CTkButton(frame, text="Guardar imagen", command=lambda: self.download_image(name, data))
        download_button.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)

        download_as = CTkButton(frame, text="Guardar como", command=lambda: self.download_as(name, data))
        download_as.pack(side=RIGHT, fill=X, expand=True, padx=5, pady=5)

    def show_message(self, message, top_frame, side):

        case = 0

        if message:
            try:
                index = message.index('>')

                if all(line.strip() == "" for line in message[index + 1:len(message)].splitlines()):
                    return -1
                else:
                    content = [line for line in message[index + 1:len(message)].splitlines() if not line.strip() == ""]
                    content = '\n\n'.join(content)
                    content = content[1:len(content)]
            except:
                case = 1
                content = message

            if case == 0:
                frame = CTkFrame(top_frame, fg_color="#232323", border_color="white", border_width=2)

                if side == "right":
                    frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='ne')
                elif side == "left":
                    frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='nw')

                label1 = CTkLabel(frame, width=600, text=message[0:index], justify=LEFT, font=('MathJax_Math', 18), anchor='w', wraplength=600)
                label1.pack(padx=20, pady=10)

                label2 = CTkLabel(frame, width=600, text=content, justify=LEFT, font=('Ariali', 15), anchor='w', wraplength=600)
                label2.pack(padx=20, pady=(5, 20))
            else:
                frame = CTkFrame(top_frame, fg_color="#232323", border_color="white", border_width=2)
                frame.pack(padx=20, pady=5, side=TOP, fill=BOTH)

                label2 = CTkLabel(frame, text=content, justify=CENTER, font=('Ariali', 15), wraplength=600)
                label2.pack(padx=20, pady=(5, 20), fill=X, expand=True)

                top_frame.update_idletasks()
                top_frame._parent_canvas.yview_moveto(1.0)

    def show_files(self, top_frame, name, data, side):

        index = name.index(':')
        username = name[0:index]
        name = name[index+1:len(name)]

        frame = CTkFrame(top_frame, fg_color="#232323", border_color="white", border_width=2)

        if side == "right":
            frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='ne')
        elif side == "left":
            frame.pack(padx=20, pady=5, side=TOP, fill=Y, anchor='nw')

        frame.configure(fg_color="#000000")

        label = CTkLabel(frame, text=username, width=300, bg_color="#000000", font=('MathJax_Math', 18), wraplength=290, justify=LEFT, anchor='w')
        label.pack(padx=5, pady=(3, 0), fill=X, expand=True)

        label_name = CTkLabel(frame, text=name, width=300, bg_color="#000000", font=('MathJax_Math', 20), wraplength=290)
        label_name.pack(padx=5)

        download_button = CTkButton(frame, text="Guardar Archivo", command=lambda: self.download_file(name, data))
        download_button.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)

        download_as = CTkButton(frame, text="Guardar como", command=lambda: self.download_as(name, data))
        download_as.pack(side=RIGHT, fill=X, expand=True, padx=5, pady=5)

    def pressed_key(self, event, client, top_frame, entry_widget):

        if event.keysym == 'Return':
            if event.state == 0x0001:

                return
            else:
                self.send_message(client, top_frame, entry_widget)
                return "break"

    def calcel_send_img(self):
        self.sending_image = False

    def calcel_send_file(self):
        self.sending_file = False

    def send_file(self, client, top_frame, frame):

        if self.sending_file:
            msg = CTkMessagebox(title="Enviando archivo", message="Espere a que finalice el envío actual o cancelelo.", icon="warning", option_1="OK", width=200)
            msg.get()
            return

        if os.name == "posix":
            path = filedialog.askopenfilename(initialdir="/home", title="Seleccione un archivo")
        else:
            try:
                path = filedialog.askopenfilename(initialdir="/Users", title="Seleccione un archivo")
            except:
                path = filedialog.askopenfilename(initialdir="/Usuarios", title="Seleccione un archivo")

        if path:
            confirm = CTkMessagebox(title="Confirmar envío", message="¿Desea enviar este archivo?", icon="question", option_1="Yes", option_2="No")
            if confirm.get() == "Yes":
                if not self.sending_file:
                    self.sending_file = True
                    try:
                        with open(path, 'r') as f:
                            total_data = f.read()

                        x = 1
                    except:
                        try:
                            with open(path, 'rb') as f:
                                total_data = f.read()

                            x = 2
                        except:
                            msg = CTkMessagebox(title="Error", message="Error al cargar el archivo.", icon="warning", option_1="OK")
                            msg.get()
                            self.sending_file = False
                            return

                    name = f"{self.username}:"
                    name += path.split('/')[-1]

                    size = os.path.getsize(path)
                    short_size = size / 8000

                    if short_size < 1:
                        short_size = 1
                    else:
                        aux = round(short_size)
                        if short_size > aux:
                            short_size = aux + 1
                        else:
                            short_size = aux

                    step = 1 / short_size
                    pro = 0

                    frame.pack_configure(pady=10)

                    button = CTkButton(frame, text="Cancelar envío", command=lambda: self.calcel_send_file())
                    button.pack(side=LEFT, fill=X)

                    progress = CTkProgressBar(frame, orientation="horizontal", mode="determinate")
                    progress.pack(side=LEFT, fill=X, expand=True, padx=10)
                    progress.update_idletasks()
                    progress.set(pro)
                    progress.update_idletasks()

                    label = CTkLabel(frame, text="Archivo")
                    label.pack(side=LEFT, padx=(0, 10), fill=X)

                    client.sendall(f"{name}".encode())
                    time.sleep(3)

                    if x == 1:
                        with open(path, 'r') as f:
                            while True:
                                time.sleep(0.1)

                                if not self.sending_file:
                                    client.sendall("END".encode())
                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    frame.pack_configure(pady=0)
                                    return

                                data = f.read(8000).encode()
                                if not data:
                                    time.sleep(3)
                                    if not self.sending_file:
                                        client.sendall("END".encode())
                                        button.destroy()
                                        progress.destroy()
                                        label.destroy()
                                        frame.configure(height=0)
                                        frame.pack_configure(pady=0)
                                        return

                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    client.sendall("FIN".encode())
                                    break
                                else:
                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                client.sendall(data)
                    elif x == 2:
                        with open(path, 'rb') as f:
                            while True:
                                time.sleep(0.1)

                                if not self.sending_file:
                                    client.sendall("END".encode())
                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    frame.pack_configure(pady=0)
                                    return

                                data = f.read(8000)
                                if not data:
                                    time.sleep(3)
                                    if not self.sending_file:
                                        client.sendall("END".encode())
                                        button.destroy()
                                        progress.destroy()
                                        label.destroy()
                                        frame.configure(height=0)
                                        frame.pack_configure(pady=0)
                                        return

                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    client.sendall("FIN".encode())
                                    break
                                else:
                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                client.sendall(data)

                    frame.pack_configure(pady=0)
                    self.show_files(top_frame, name, total_data, "right")
                    top_frame.update_idletasks()
                    top_frame._parent_canvas.yview_moveto(1.0)
                    self.sending_file = False

    def before_send_file(self, client, top_frame, frame):

        thread = threading.Thread(target=self.send_file, args=(client, top_frame, frame))
        thread.daemon = True
        thread.start()

    def send_image(self, client, top_frame, frame):

        if self.sending_image:
            msg = CTkMessagebox(title="Enviando imagen", message="Espere a que finalice el envío actual o cancelelo.", icon="warning", option_1="OK", width=200)
            msg.get()
            return

        if os.name == "posix":
            path = filedialog.askopenfilename(initialdir="/home", title="Image selection")
        else:
            try:
                path = filedialog.askopenfilename(initialdir="/Users")
            except:
                path = filedialog.askopenfilename(initialdir="/Usuarios")

        if path:
            if path[-3:len(path)] == "png" or path[-3:len(path)] == "jpg" or path[-4:len(path)] == "jpeg":
                confirm = CTkMessagebox(title="Confirmar envío", message="¿Desea enviar esta imagen?", icon="question", option_1="Yes", option_2="No")
                if confirm.get() == "Yes":
                    if not self.sending_image:
                        self.sending_image = True
                        with open(path, 'rb') as f:
                            total_data = f.read()

                        name = f"{self.username}:"
                        name += path.split('/')[-1]
                        size = os.path.getsize(path)
                        short_size = size / 8000

                        if short_size < 1:
                            short_size = 1
                        else:
                            aux = round(short_size)
                            if short_size > aux:
                                short_size = aux + 1
                            else:
                                short_size = aux

                        step = 1 / short_size
                        pro = 0

                        button = CTkButton(frame, text="Cancelar envío", command=lambda: self.calcel_send_img())
                        button.pack(side=LEFT, fill=X)

                        progress = CTkProgressBar(frame, orientation="horizontal", mode="determinate")
                        progress.pack(side=LEFT, fill=X, expand=True, padx=10)
                        progress.update_idletasks()
                        progress.set(pro)
                        progress.update_idletasks()

                        label = CTkLabel(frame, text="Imagen")
                        label.pack(side=LEFT, padx=(0, 10), fill=X)

                        client.sendall(f"{name}".encode())
                        time.sleep(3)

                        with open(path, 'rb') as f:
                            while True:
                                time.sleep(0.1)

                                data = f.read(8000)
                                if not self.sending_image:
                                    client.sendall("END".encode())
                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    return

                                if not data:
                                    time.sleep(3)
                                    if not self.sending_image:
                                        client.sendall("END".encode())
                                        button.destroy()
                                        progress.destroy()
                                        label.destroy()
                                        frame.configure(height=0)
                                        return

                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                    client.sendall("FIN".encode())
                                    button.destroy()
                                    progress.destroy()
                                    label.destroy()
                                    frame.configure(height=0)
                                    break
                                else:
                                    progress.set(pro)
                                    pro += step
                                    progress.update_idletasks()

                                client.sendall(data)

                        self.show_image(top_frame, "right", name, total_data)

                        top_frame.update_idletasks()
                        top_frame._parent_canvas.yview_moveto(1.0)

                        self.sending_image = False
            else:
                msg = CTkMessagebox(title="Archivo inválido", message="Seleccione una imagen png, jpg o jpeg.", icon="warning", option_1="OK")
                msg.get()
                return

    def before_send_image(self, client, top_frame, frame):

        thread = threading.Thread(target=self.send_image, args=(client, top_frame, frame))
        thread.daemon = True
        thread.start()

    def send_message(self, client, top_frame, entry_widget):

        message = entry_widget.get("1.0", END)

        if not message:
            return

        message = f"\n{self.username} > {message}\n"

        x = self.show_message(message, top_frame, "right")

        entry_widget.delete("1.0", END)

        if x == -1:
            return

        client.sendall(message.encode())
        top_frame.update_idletasks()
        top_frame._parent_canvas.yview_moveto(1.0)

    def show_users(self, users):

        users = users.split(',')

        if self.users:
            for user in self.users:
                    user.destroy()

            self.users = []

        for user in users:
            width = 15
            if len(user) > 15:
                user = user[0:13].strip()
                user += '...'
            box = CTkFrame(self.FrameRight, height=30, fg_color='#2E2E2E')
            box.pack(fill=X, padx=10, pady=2)
            active = CTkLabel(box, fg_color="green", corner_radius=50, text='')
            active.place(relx=0.2, rely=0.5, relwidth=0.1, relheight=0.6, anchor='e')
            b = CTkLabel(box, text=user, font=('Arial', width), justify=CENTER, text_color='white')
            b.place(relx=0.3, rely=0.5, anchor="w")
            self.users.append(box)

    def verify_users(self):
        if self.active_listening and self.voice_users_cont < self.voice_users_cont_last:
            pygame.mixer.init()
            pygame.mixer.music.load('./sounds/join_call.mp3')
            pygame.mixer.music.play()
            self.voice_users_cont_last = self.voice_users_cont
        elif self.voice_users_cont_last != 0:
            if self.active_listening and self.voice_users_cont > self.voice_users_cont_last:
                pygame.mixer.init()
                pygame.mixer.music.load('./sounds/leave_call.mp3')
                pygame.mixer.music.play()
                self.voice_users_cont_last = self.voice_users_cont

    def show_voice_users(self, users, left_center):

        if not users == "NULL":
            users = users.split(',')

            if self.users_voice:
                for user in self.users_voice:
                        user.destroy()

                self.users_voice = []

            self.verify_users()
            self.voice_users_cont += 1

            for user in users:
                width = 15
                if len(user) > 15:
                    user = user[0:13].strip()
                    user += '...'
                box = CTkFrame(left_center, height=30, fg_color='#2E2E2E')
                box.pack(fill=X, padx=10, pady=2)
                active = CTkLabel(box, fg_color="green", corner_radius=50, text='')
                active.place(relx=0.2, rely=0.5, relwidth=0.1, relheight=0.6, anchor='e')
                b = CTkLabel(box, text=user, font=('Arial', width), justify=CENTER, text_color='white')
                b.place(relx=0.3, rely=0.5, anchor="w")
                self.users_voice.append(box)
        else:
            if self.users_voice:
                for user in self.users_voice:
                        user.destroy()

    def recv_images(self, images_socket, top_frame):
        with images_socket as client:

            while True:
                try:
                    try:
                        name = client.recv(8000).decode()
                    except:
                        continue

                    if not name:
                        break

                    x = 0
                    while True:
                        data_d = client.recv(8000)

                        try:
                            data_d = data_d.decode()
                            if data_d == "FIN":
                                break
                        except:
                            x += 1

                            if x == 1:
                                data = data_d
                            else:
                                data += data_d

                            continue

                    self.show_image(top_frame, "left", name, data)
                except:
                    break

    def recv_files(self, files_socket, top_frame):

        with files_socket as client:

            while True:
                try:
                    try:
                        name = client.recv(8000).decode()
                    except:
                        continue

                    if not name:
                        break

                    data = 'p'
                    x = 0
                    while data:
                        data_d = client.recv(8000)

                        try:
                            data_d = data_d.decode()
                            if data_d == "FIN":
                                break
                            elif data == 'p':
                                data = ''
                        except:
                            x += 1

                            if x == 1:
                                data = data_d
                            else:
                                data += data_d

                            continue

                        data += data_d

                    self.show_files(top_frame, name, data, "left")
                except:
                    break

    def recv_usrs(self, usrs_socket):

        with usrs_socket as usrs:

            text_box = CTkFrame(self.FrameRight)
            text_box.pack(fill=X, pady=20)
            label = CTkLabel(text_box, text="Usuarios activos", justify=CENTER, font=('MathJax_Math', 24))
            label.pack()

            while True:
                try:
                    users = usrs_socket.recv(1024*1024).decode()

                    if not users:
                        break

                    self.show_users(users)
                except:
                    break

    def recv_voice_usrs(self, voices_socket, left_center):

        with voices_socket as usrs:

            while True:
                try:
                    users = usrs.recv(1024*1024).decode()

                    if not users:
                        break

                    self.show_voice_users(users, left_center)
                except:
                    break


    def recv_message(self, client_socket, top_frame):

        while True:
            try:
                message = client_socket.recv(8000).decode()

                if not message:
                    break

                if message == "CLOSE":
                    pass

                self.show_message(message, top_frame, "left")
            except:
                break
