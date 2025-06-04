#!/usr/bin/env python3

import threading
import socket
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from client import Client
from PIL import Image
import ssl

class App:

    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.connection = False
        self.button_pressed = None
        self.quit = False
        self.config_window = None

        self.client_app() 

    def quit_app(self, app):
        self.button_pressed.set(True)
        app.destroy()
        exit()

    def read_data(self):

        try:
            with open('./host', 'r') as file:
                data = file.read().split(' ')

            self.HOST = data[0]
            self.PORT = int(data[1])
        except:
            pass

    def write_data(self, app, host, port, widgets):
        global HOST
        global PORT

        host = host.get()
        port = port.get()

        try:
            HOST = host.strip()
            PORT = int(port.strip())
            with open('./host', 'w') as file:
                file.write(f"{HOST} {PORT}")

            for widget in widgets:
                widget.destroy()

            self.read_data()

            self.button_pressed.set(True)
        except:
            msg = CTkMessagebox(master=app, title="Error de información", message="Introduzca correctamente la información.", icon="warning", option_1="Intentar nuevamente", option_2="Salir")
            option = msg.get()

            if option == "Intentar nuevamente":
                pass
            else:
                self.button_pressed.set(True)
                app.destroy()
                exit(0)

    def get_data(self, app):
        app.geometry('800x700')
        app.title('Información de conexión')
        app.after(201, lambda: app.iconbitmap('./icon/main.ico'))
        app.configure(fg_color="#6486a5")

        frame = CTkFrame(app, fg_color="#2E2E2E")
        frame.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=1, anchor="center")

        frame_top = CTkFrame(frame, fg_color='transparent')
        frame_top.pack(fill=X, pady=100)

        title_label = CTkLabel(frame_top, text="Datos del servidor", font=('MathJax_Math', 30))
        title_label.pack(fill=X)

        frame_bottom = CTkFrame(frame, fg_color='transparent')
        frame_bottom.pack(fill=BOTH, expand=True)

        host_label = CTkLabel(frame_bottom, text="HOST", font=('MathJax_Math', 25), justify=LEFT)
        host_label.pack(fill=X, anchor='w')

        host_entry = CTkEntry(frame_bottom, placeholder_text="Ingrese la ip del servidor...")
        host_entry.pack(fill=X, pady=20, padx=30)

        port_label = CTkLabel(frame_bottom, text="PUERTO", font=('MathJax_Math', 25), justify=LEFT)
        port_label.pack(fill=X, anchor='w')

        port_entry = CTkEntry(frame_bottom, placeholder_text="Ingrese el puerto del servidor...")
        port_entry.pack(fill=X, pady=20, padx=30)

        frame_buttons = CTkFrame(frame_bottom, fg_color='transparent')
        frame_buttons.pack(fill=X, pady=(50, 0), padx=30)

        save_button = CTkButton(frame_buttons, text="Guardar", font=('MathJax_Math', 20))
        save_button.place(relx=0, rely=0, relwidth=0.45, relheight=0.2, anchor='nw')

        exit_button = CTkButton(frame_buttons, text="Salir", font=('MathJax_Math', 20), command=lambda: self.quit_app(app))
        exit_button.place(relx=1, rely=0, relwidth=0.45, relheight=0.2, anchor='ne')

        widgets = [frame, frame_top, title_label, frame_bottom, host_label, host_entry, port_label, port_entry, frame_buttons, save_button, exit_button]
        save_button.configure(command=lambda: self.write_data(app, host_entry, port_entry, widgets))

    def on_close_window(self):
        self.config_window.destroy()
        self.config_window = None

    def config(self, app):
        if not self.config_window:
            self.config_window = CTkToplevel(app)
            self.config_window.geometry("1250x600")
            self.config_window.protocol("WM_DELETE_WINDOW", self.on_close_window)

    def client_app(self):
        set_appearance_mode("dark")
        set_default_color_theme("dark-blue")
        app = CTk()
        app.geometry("1400x700")
        app.title("Didiscord")
        app.after(201, lambda: app.iconbitmap('./icon/main.ico'))

        self.button_pressed = StringVar(value=None)

        while not self.connection:
            try:
                user = Client(self.HOST, self.PORT)
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(1)
                client_socket.connect((user.HOST, user.PORT))
                client_socket.settimeout(None)
                self.connection = True
            except:
                msg = CTkMessagebox(title="Error de conexión", message="Es posible que los datos del servidor sean incorrectos.", icon="warning", option_1="OK")
                d = msg.get()
                self.get_data(app)
                app.wait_variable(self.button_pressed)

        app.geometry("1400x700")
        app.title("Didiscord")
        app.after(201, lambda: app.iconbitmap('./icon/main.ico'))
        app.configure(fg_color="#2E2E2E")

        while True:
            dialog = CTkInputDialog(text="Ingrese su alias:")
            dialog.title("Username")
            username = dialog.get_input()

            if username:
                user.username = username
                break
            elif username == None:
                app.destroy()
                return

        user.username = user.username.capitalize()

        user.FrameLeft = CTkFrame(app)
        user.FrameCenter = CTkFrame(app)
        user.FrameRight = CTkScrollableFrame(app)

        client_socket.sendall(user.username.encode())

        usrs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        usrs_socket.connect((user.HOST, user.USERS_PORT))

        file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        file_socket.connect((user.HOST, user.FILES_PORT))

        image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        image_socket.connect((user.HOST, user.IMAGES_PORT))

        voices_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        voices_socket.connect((user.HOST, user.VOICES_PORT))

        # LEFT
        user.FrameLeft.place(relx=0, rely=0, relwidth=0.15, relheight=1.0, anchor="nw")
        left_top = CTkFrame(user.FrameLeft)
        left_center = CTkScrollableFrame(user.FrameLeft)
        left_bottom = CTkFrame(user.FrameLeft)

        left_top.place(relx=0, rely=0, relwidth=1, relheight=0.15, anchor="nw")
        left_center.place(relx=0.5, rely=0.5, relwidth=1, relheight=0.7, anchor="center")
        left_bottom.place(relx=1, rely=1, relwidth=1, relheight=0.15, anchor="se")

        top_label = CTkLabel(left_top, text="Chat de voz", bg_color='transparent', font=('MathJax_Math', 25))
        top_label.pack(padx=10, pady=10, anchor="center")

        icon_voice_chat = CTkImage(light_image=Image.open('./icon/voice-channel-light.png'), dark_image=Image.open('./icon/voice-channel-dark.png'), size=(35, 35))
        top_button = CTkButton(left_top, image=icon_voice_chat, text="Chat de voz", fg_color='transparent', hover_color="gray", corner_radius=50, font=('Arial', 20))
        top_button.pack(padx=10, pady=10, fill=BOTH, expand=True)

        bottom_frame1 = CTkFrame(left_bottom, fg_color='transparent')
        bottom_frame1.pack(padx=(10, 0), pady=(20, 5), fill=X)

        width = 24

        username = user.username

        if len(user.username) > 12:
            username = user.username[0:11] + '...'
            width = 22

        username_label = CTkLabel(bottom_frame1, text=username, font=('MathJax_Math', width), justify=LEFT, width=100)
        username_label.pack(side=LEFT, anchor='w', fill=X)

        icon_config = CTkImage(light_image=Image.open('./icon/config-light.png'), dark_image=Image.open('./icon/config-dark.png'), size=(25, 25))
        config_button = CTkButton(bottom_frame1, image=icon_config, text='', fg_color='transparent', corner_radius=100, width=1)
        config_button.pack(side=RIGHT, padx=(10, 0))

        bottom_frame2 = CTkFrame(left_bottom, fg_color='transparent')
        bottom_frame2.pack(fill=X)

        icon_mic = CTkImage(light_image=Image.open('./icon/microfone-light.png'), dark_image=Image.open('./icon/microfone-dark.png'), size=(25, 25))
        mic_button = CTkButton(bottom_frame2, text="", image=icon_mic, width=1, fg_color='transparent', corner_radius=100)
        mic_button.pack(side=LEFT, padx=(0, 5), pady=(10, 0))

        icon_sound = CTkImage(light_image=Image.open('./icon/sound-light.png'), dark_image=Image.open('./icon/sound-dark.png'), size=(25, 25))
        sound_button = CTkButton(bottom_frame2, text="", image=icon_sound, width=1, fg_color='transparent', corner_radius=100)
        sound_button.configure(command=lambda: user.sound(sound_button, mic_button, icon_sound))
        sound_button.pack(side=LEFT, pady=(10, 0))

        top_button.configure(command=lambda: user.active_voice(bottom_frame2))
        mic_button.configure(command=lambda: user.mic(mic_button, icon_mic, sound_button, icon_sound))
        config_button.configure(command=lambda: self.config(app))

        # CENTER
        user.FrameCenter.place(relx=0.5, rely=0.5, relwidth=0.70, relheight=1.0, anchor="center")


        top_frame = CTkScrollableFrame(user.FrameCenter, fg_color="#2E2E2E")
        top_frame.pack(padx=10, pady=5, fill=BOTH, expand=True)

        center_frame_image = CTkFrame(user.FrameCenter, height=0)
        center_frame_image.pack(fill=X, padx=10)

        center_frame_file = CTkFrame(user.FrameCenter, height=0)
        center_frame_file.pack(fill=X, padx=10)

        frame = CTkFrame(user.FrameCenter)
        frame.pack(fill=X, padx=10, pady=(5,10))

        upload = CTkFrame(frame)
        upload.pack(side=LEFT, fill=BOTH, padx=(0,10))

        entry_widget = CTkTextbox(frame, height=100)
        entry_widget.bind('<KeyPress>', lambda event: user.pressed_key(event, client_socket, top_frame, entry_widget))
        entry_widget.pack(side=LEFT, fill=BOTH, expand=True)

        file_button = CTkButton(upload, text="Archivo", height=45, command=lambda: user.before_send_file(file_socket, top_frame, center_frame_file))
        file_button.pack(pady=(0,6))

        img_button = CTkButton(upload, text="Imagen", height=45, command=lambda: user.before_send_image(image_socket, top_frame, center_frame_image))
        img_button.pack()

        send_widget = CTkButton(frame, text="Enviar", command=lambda: user.send_message(client_socket, top_frame, entry_widget))
        send_widget.pack(side=RIGHT, padx=(10,0), fill=Y)

        # RIGHT
        user.FrameRight.place(relx=1, rely=0, relwidth=0.15, relheight=1.0,anchor="ne")

        thread1 = threading.Thread(target=user.recv_message, args=(client_socket, top_frame))
        thread1.daemon = True
        thread1.start()

        thread2 = threading.Thread(target=user.recv_usrs, args=(usrs_socket,))
        thread2.daemon = True
        thread2.start()

        thread3 = threading.Thread(target=user.recv_files, args=(file_socket, top_frame))
        thread3.daemon = True
        thread3.start()

        thread4 = threading.Thread(target=user.recv_images, args=(image_socket, top_frame))
        thread4.daemon = True
        thread4.start()

        thread5 = threading.Thread(target=user.recv_voice_usrs, args=(voices_socket, left_center))
        thread5.daemon = True
        thread5.start()

        app.mainloop()
