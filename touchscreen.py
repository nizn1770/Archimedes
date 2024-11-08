import config
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage



def init_touchscreen(logger):
    global root

    app = Application(logger)
    app.mainloop()


class Application(tk.Tk):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.logger.info("Archimedes initialized")

        global horizontal_len, vertical_len

        self.title("Archimedes")

        self.attributes("-fullscreen", True)

        self.bind("<Escape>", self.exit_fullscreen)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.hor = InputMeasure(self, "Horizontal")
        self.hor.grid(row=0, column=0, sticky="nsew")
        self.hor.feet.focus_set()

        self.vert = InputMeasure(self, "Vertical")
        self.vert.grid(row=1, column=0, sticky="nsew")

        submit = ttk.Button(self, text="Send Cut", command=self.send_cuts)
        submit.grid(row=2, column=0, sticky="nsew")

        self.keyboard = KeyBoard(self, [self.hor, self.vert])
        self.keyboard.grid(row=0, column=1, rowspan=3, sticky="nsew")

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)

    def send_cuts(self):
        if not self.validate_inputs():
            print("Invalid inputs")
        else:
            horizontal_len, vertical_len = self.combine_vals()
            if horizontal_len > config.MAX_HORIZONTAL:
                print("Horizontal cut is too large")
            elif vertical_len > config.MAX_VERTICAL:
                print("Vertical cut is too large.")
            else:
                print("Horizontal cut length: ", horizontal_len, "ft")
                print("Vertical cut length: ", vertical_len, "ft")

        self.clear_entries()
        

    def combine_vals(self):
        hor_feet = int(self.hor.feet.get())
        hor_inch = int(self.hor.inch.get())
        hor_frac = int(self.hor.frac.get())

        vert_feet = int(self.vert.feet.get())
        vert_inch = int(self.vert.inch.get())
        vert_frac = int(self.vert.frac.get())

        hor_len = hor_feet + hor_inch * (1/12) + hor_frac * (1/16)
        ver_len = vert_feet + vert_inch * (1/12) + vert_frac * (1/16)

        return hor_len, ver_len

    #Method to check if the values that are input have data and are numbers
    def validate_inputs(self):
        vals = [self.hor.feet.get(), self.hor.inch.get(), self.hor.frac.get(),
        self.vert.feet.get(), self.vert.inch.get(), self.vert.frac.get()]

        for val in vals:
            if not val:
                print("Empty String")
                return False
            if not val.isnumeric():
                print("Invalid inputs: ", val)
                return False
        return True

    #Method to clear text entries after the send cut button has been pressed
    def clear_entries(self):
        for input_measure in [self.hor, self.vert]:
            input_measure.feet.delete(0, tk.END)
            input_measure.inch.delete(0, tk.END)
            input_measure.frac.delete(0, tk.END)

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

<<<<<<< Updated upstream
        #image = PhotoImage(file=r"C:\Users\nizni\University of St. Thomas\Archimedes - Code\Archimedes\images\delete.png")
        # add after text for image on image=image,
        self.delete = ttk.Button(self, text="D",  command=self.delete_text)
=======
        self.delete = ttk.Button(self, text="D", command=self.delete_text)
>>>>>>> Stashed changes
        self.delete.grid(row=3, column=2, sticky="nsew")
        #self.delete.image = image

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