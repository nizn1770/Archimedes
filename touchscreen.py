import tkinter as tk
from tkinter import ttk


def init_touchscreen():
    global root

    app = Application()
    app.mainloop()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Archimedes")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=3)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)
        
        hor = InputMeasure(self, "Horizontal")
        hor.grid(row=0, column=0, sticky="nsew")

        vert = InputMeasure(self, "Vertical")
        vert.grid(row=1, column=0, sticky="nsew")

        submit = ttk.Button(self, text="Send Cut")
        submit.grid(row=2, column=0, sticky="nsew")
    


class InputMeasure(ttk.Frame):
    def __init__(self, parent, title_text):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.title = ttk.Label(self, text=title_text, justify='center')
        self.title.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.feet = ttk.Entry(self)
        self.feet.grid(row=1, column=0, sticky="ew")

        self.feet_label = ttk.Label(self, text="Feet", justify='center')
        self.feet_label.grid(row=2, column=0, sticky="ew")

        self.inch = ttk.Entry(self)
        self.inch.grid(row=1, column=1, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", justify='center')
        self.inch_label.grid(row=2, column=1, sticky="ew")

        self.frac = ttk.Entry(self)
        self.frac.grid(row=1, column=2, sticky="ew")

        self.frac_label = ttk.Label(self, text="Fraction", justify='center')
        self.frac_label.grid(row=2, column=2, sticky="ew")

class KeyBoard(ttk.Frame):
    def __init__(self, parent, num):
        super().__init__(parent)

        self.btn = ttk.Button(self, text=num)
        self.btn.grid(row=0, column=0, sticky="nsew")

