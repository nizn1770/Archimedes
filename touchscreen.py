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

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        len = InputMeasure(self, "Length")
        len.grid(row=0, column=0, sticky="nsew")

        wid = InputMeasure(self, "Width")
        wid.grid(row=0, column=0, sticky="nsew")

class InputMeasure(ttk.frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.title = ttk.Label(self)


        self.feet = ttk.Entry(self)
        self.feet.grid(row=1, column=0, sticky="ew")

        self.feetLabel = ttk.Label(self, text="Feet")
        self.feetLabel.grid(row=2, column=0, sticky="ew")

        self.inch = ttk.Entry(self)
        self.inch.grid(row=1, column=1, sticky="ew")

        self.inchLabel = ttk.Label(self, text="Inches")
        self.inchLabel.grid(row=2, column=1, sticky="ew")

        self.frac = ttk.Entry(self)
        self.frac.grid(row=1, column=2, sticky="ew")

        self.fracLabel = ttk.Label(self, text="Fraction")
        self.fracLabel.grid(row=2, column=2, sticky="ew")



