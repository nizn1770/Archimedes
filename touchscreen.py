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

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
        hor = InputMeasure(self, "Horizontal")
        hor.grid(row=0, column=0, sticky="nsew")
        hor.feet.focus_set()

        vert = InputMeasure(self, "Vertical")
        vert.grid(row=1, column=0, sticky="nsew")

        submit = ttk.Button(self, text="Send Cut")
        submit.grid(row=2, column=0, sticky="nsew")

        keyboard = KeyBoard(self, [hor, vert])
        keyboard.grid(row=0, column=1, rowspan=3, sticky="nsew")



class InputMeasure(ttk.Frame):
    def __init__(self, parent, title_text):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.title = ttk.Label(self, text=title_text, font=('Arial 16'))
        self.title.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.feet = ttk.Entry(self, font=('Arial 12'))
        self.feet.grid(row=1, column=0, sticky="ew")

        self.feet_label = ttk.Label(self, text="Feet", font=('Arial 12'))
        self.feet_label.grid(row=2, column=0, sticky="n")

        self.inch = ttk.Entry(self, font=('Arial 12'))
        self.inch.grid(row=1, column=1, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", font=('Arial 12'))
        self.inch_label.grid(row=2, column=1, sticky="n")

        self.frac = ttk.Entry(self, font=('Arial 12'))
        self.frac.grid(row=1, column=2, sticky="ew")

        self.frac_label = ttk.Label(self, text="Fraction", font=('Arial 12'))
        self.frac_label.grid(row=2, column=2, sticky="n")

class KeyBoard(ttk.Frame):
    def __init__(self, parent, input_measures):
        super().__init__(parent)
        
        self.input_measures = input_measures
        self.active_entry = input_measures[0].feet

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.one = ttk.Button(self, text="1", command=lambda: self.insert_text(1))
        self.one.grid(row=0, column=0, sticky="nsew")

        self.two = ttk.Button(self, text="2", command=lambda: self.insert_text(2))
        self.two.grid(row=0, column=1, sticky="nsew")

        self.three = ttk.Button(self, text="3", command=lambda: self.insert_text(3))
        self.three.grid(row=0, column=2, sticky="nsew")

        self.four = ttk.Button(self, text="4", command=lambda: self.insert_text(4))
        self.four.grid(row=1, column=0, sticky="nsew")

        self.five = ttk.Button(self, text="5", command=lambda: self.insert_text(5))
        self.five.grid(row=1, column=1, sticky="nsew")

        self.six = ttk.Button(self, text="6", command=lambda: self.insert_text(6))
        self.six.grid(row=1, column=2, sticky="nsew")

        self.seven = ttk.Button(self, text="7", command=lambda: self.insert_text(7))
        self.seven.grid(row=2, column=0, sticky="nsew")

        self.eight = ttk.Button(self, text="8", command=lambda: self.insert_text(8))
        self.eight.grid(row=2, column=1, sticky="nsew")

        self.nine = ttk.Button(self, text="9", command=lambda: self.insert_text(9))
        self.nine.grid(row=2, column=2, sticky="nsew")

        self.next = ttk.Button(self, text="N", command=self.switch_entry)
        self.next.grid(row=3, column=0, sticky="nsew")

        self.zero = ttk.Button(self, text="0", command=lambda: self.insert_text(0))
        self.zero.grid(row=3, column=1, sticky="nsew")

        self.delete = ttk.Button(self, text="D", command=self.delete_text)
        self.delete.grid(row=3, column=2, sticky="nsew")

    def insert_text(self, char):
        if self.active_entry:
            self.active_entry.insert(tk.END, str(char))

    def delete_text(self):
        current_text = self.active_entry.get()

        if current_text:
            self.active_entry.delete(len(current_text)-1,tk.END)

    def switch_entry(self):
        if self.active_entry == self.input_measures[0].feet:
            self.active_entry = self.input_measures[0].inch
        elif self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[0].frac
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[1].feet  
        elif self.active_entry == self.input_measures[1].feet:
            self.active_entry = self.input_measures[1].inch
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[1].frac
        else:
            self.active_entry = self.input_measures[0].feet  