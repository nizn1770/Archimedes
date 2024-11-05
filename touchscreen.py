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

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        
        hor = InputMeasure(self, "Horizontal")
        hor.grid(row=0, column=0, sticky="nsew")

        vert = InputMeasure(self, "Vertical")
        vert.grid(row=1, column=0, sticky="nsew")

        submit = ttk.Button(self, text="Send Cut", command=self.send_cut)
    


class InputMeasure(ttk.frame):
    def __init__(self, parent, title_text):
        super().__init__(parent)

        self.title = ttk.Label(self, text=title_text, justify="center")
        self.title.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.feet = ttk.Entry(self)
        self.feet.grid(row=1, column=0, sticky="ew")

        self.feet_label = ttk.Label(self, text="Feet")
        self.feet_label.grid(row=2, column=0, sticky="ew")

        self.inch = ttk.Entry(self)
        self.inch.grid(row=1, column=1, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches")
        self.inch_label.grid(row=2, column=1, sticky="ew")

        self.frac = ttk.Entry(self)
        self.frac.grid(row=1, column=2, sticky="ew")

        self.frac_label = ttk.Label(self, text="Fraction")
        self.frac_label.grid(row=2, column=2, sticky="ew")

