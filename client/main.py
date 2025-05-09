#!/usr/bin/env python3

from display import App
from customtkinter import *
from CTkMessagebox import CTkMessagebox

set_appearance_mode("dark")
set_default_color_theme("dark-blue")
HOST = ''
PORT = 0

def read_data():
    global HOST
    global PORT

    try:
        with open('./host', 'r') as file:
            data = file.read().split(' ')

        HOST = data[0]
        PORT = int(data[1])
    except:
        HOST = 'IP'
        PORT = 8080
        with open('./host', 'w') as file:
            file.write(f"{HOST} {PORT}")

def main():
    read_data()

    app = App(HOST, PORT)

if __name__ == '__main__':
    main()
