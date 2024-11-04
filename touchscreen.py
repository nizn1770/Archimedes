import tkinter as tk

def init_touchscreen():
    global root

    app = Application()
    app.mainloop()


class Application(tk.TK):
    def __init__(self):
        super().__init__()
        self.title("Archimedes")

