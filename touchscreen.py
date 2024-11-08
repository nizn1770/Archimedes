import config
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from utils.style import apply_styles


def init_touchscreen(logger):
    global root

    app = Application(logger)
    app.mainloop()


class Application(tk.Tk):
    def __init__(self, logger):
        super().__init__()

        self.logger = logger
        self.logger.info("Archimedes initialized")

        self.title("Archimedes")

        self.attributes("-fullscreen", True)
        self.bind("<Escape>", self.exit_fullscreen)

        apply_styles(self)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.inputs = BuildInputs(self)
        self.inputs.grid(row=0, column=0, sticky='nsew')

        self.keyboard = KeyBoard(self, [self.inputs.hor, self.inputs.vert])
        self.keyboard.grid(row=0, column=1, sticky="nsew")

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)

    def send_cuts(self):
        self.validate_inputs()
        self.clear_entries()
        self.keyboard.reset_entry()
        
    def validate_inputs(self):
        self.check_numeric()
        self.check_size()

    def check_numeric(self):
        vals = [self.hor.feet.get(), self.hor.inch.get(), self.hor.frac.get(),
        self.vert.feet.get(), self.vert.inch.get(), self.vert.frac.get()]

        for val in vals:
            if not val:
                self.logger.info("String was empty. Values are invalid.")
                print("Empty String")
                return False
            if not val.isnumeric():
                self.logger.info("String was not a valid numeric number.  Values are invalid.")
                print("Invalid inputs: ", val)
                return False
        return True
    
    def check_size(self):
        self.horizontal_len, self.vertical_len = self.combine_vals()
        if self.horizontal_len > config.MAX_HORIZONTAL and self.vertical_len > config.MAX_VERTICAL:
            self.logger.info(f"Horizontal: {self.horizontal_len} is greater than {config.MAX_HORIZONTAL}\nVertical: {self.vertical_len} is greater than {config.MAX_VERTICAL}")
            print("Horizontal and vertical cuts are too large")
        elif self.horizontal_len > config.MAX_HORIZONTAL:
            self.logger.info(f"Horizontal: {self.horizontal_len} is greater than {config.MAX_HORIZONTAL}")
            print("Horizontal cut is too large")
        elif self.vertical_len > config.MAX_VERTICAL:
            self.logger.info(f"Vertical: {self.vertical_len} is greater than {config.MAX_VERTICAL}")
            print("Vertical cut is too large.")
        else:
            self.logger.info(f"Horizontal: {self.horizontal_len}\nVertical: {self.vertical_len}")
            print("Horizontal cut length: ", self.horizontal_len, "ft")
            print("Vertical cut length: ", self.vertical_len, "ft")

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
    
    #Method to clear text entries after the send cut button has been pressed
    def clear_entries(self):
        for input_measure in [self.hor, self.vert]:
            input_measure.feet.delete(0, tk.END)
            input_measure.inch.delete(0, tk.END)
            input_measure.frac.delete(0, tk.END)

class BuildInputs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
        self.hor = InputMeasure(self, "Horizontal")
        self.hor.grid(row=0, column=0, sticky="nsew")
        self.hor.feet.focus_set()

        self.vert = InputMeasure(self, "Vertical")
        self.vert.grid(row=1, column=0, sticky="nsew")

        submit = ttk.Button(self, text="Send Cut", command=self.parent.send_cuts)
        submit.grid(row=2, column=0, sticky="nsew")

class InputMeasure(ttk.Frame):
    def __init__(self, parent, title_text):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)

        self.title = ttk.Label(self, text=title_text, style='EntryTitle.TLabel')
        self.title.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.feet = ttk.Entry(self, font=('Arial 16'))
        self.feet.grid(row=1, column=0, sticky="ew")

        self.feet_label = ttk.Label(self, text="Feet", style='EntryLabel.TLabel')
        self.feet_label.grid(row=2, column=0, sticky="n")

        self.inch = ttk.Entry(self, font=('Arial 16'))
        self.inch.grid(row=1, column=1, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", style='EntryLabel.TLabel')
        self.inch_label.grid(row=2, column=1, sticky="n")

        self.frac = ttk.Entry(self, font=('Arial 16'))
        self.frac.grid(row=1, column=2, sticky="ew")

        self.frac_label = ttk.Label(self, text="Fraction", style='EntryLabel.TLabel')
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

        self.one = ttk.Button(self, text="1", style='Key.TButton', command=lambda: self.insert_text(1))
        self.one.grid(row=0, column=0, sticky="nsew")

        self.two = ttk.Button(self, text="2", style='Key.TButton', command=lambda: self.insert_text(2))
        self.two.grid(row=0, column=1, sticky="nsew")

        self.three = ttk.Button(self, text="3", style='Key.TButton', command=lambda: self.insert_text(3))
        self.three.grid(row=0, column=2, sticky="nsew")

        self.four = ttk.Button(self, text="4", style='Key.TButton', command=lambda: self.insert_text(4))
        self.four.grid(row=1, column=0, sticky="nsew")

        self.five = ttk.Button(self, text="5", style='Key.TButton', command=lambda: self.insert_text(5))
        self.five.grid(row=1, column=1, sticky="nsew")

        self.six = ttk.Button(self, text="6", style='Key.TButton', command=lambda: self.insert_text(6))
        self.six.grid(row=1, column=2, sticky="nsew")

        self.seven = ttk.Button(self, text="7", style='Key.TButton', command=lambda: self.insert_text(7))
        self.seven.grid(row=2, column=0, sticky="nsew")

        self.eight = ttk.Button(self, text="8", style='Key.TButton', command=lambda: self.insert_text(8))
        self.eight.grid(row=2, column=1, sticky="nsew")

        self.nine = ttk.Button(self, text="9", style='Key.TButton', command=lambda: self.insert_text(9))
        self.nine.grid(row=2, column=2, sticky="nsew")

        self.next = ttk.Button(self, text="N", style='Key.TButton', command=self.switch_entry)
        self.next.grid(row=3, column=0, sticky="nsew")

        self.zero = ttk.Button(self, text="0", style='Key.TButton', command=lambda: self.insert_text(0))
        self.zero.grid(row=3, column=1, sticky="nsew")

        #image = PhotoImage(file=r"C:\Users\nizni\University of St. Thomas\Archimedes - Code\Archimedes\images\delete.png")
        # add after text for image on image=image,
        self.delete = ttk.Button(self, text="D", style='Key.TButton', command=self.delete_text)
        self.delete.grid(row=3, column=2, sticky="nsew")
        #self.delete.image = image

    def insert_text(self, char):
        if self.active_entry:
            self.active_entry.insert(tk.END, str(char))
            self.active_entry.focus_set()

    def delete_text(self):
        current_text = self.active_entry.get()

        if current_text:
            self.active_entry.delete(len(current_text)-1,tk.END)

    def reset_entry(self):
        self.active_entry = self.input_measures[0].feet
        self.active_entry.focus_set()

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

        self.active_entry.focus_set()