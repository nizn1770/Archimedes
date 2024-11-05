import tkinter as tk
from tkinter import ttk


def init_touchscreen():
    global root

    app = Application()
    app.mainloop()


class Application(tk.TK):
    def __init__(self):
        super().__init__()
        self.title("Archimedes")

class Input(ttk.frame, name):


