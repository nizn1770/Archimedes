import sys
import config
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox



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
        self.bind("Q", self.quit_program)

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
    
    def quit_program(self, event=None):
        sys.exit(0)

    def send_cuts(self):
        self.validate_inputs()
        self.clear_entries()
        self.keyboard.reset_entry()
        
    def validate_inputs(self):
        self.get_vals()
        self.check_numeric()
        self.check_size()

    def get_vals(self):
        self.vals = [self.hor.feet.get(), self.hor.inch.get(), self.hor.frac.get(),
        self.vert.feet.get(), self.vert.inch.get(), self.vert.frac.get()]

    def check_numeric(self):
        for i in range(0,6):
            if self.vals[i]:
                if not self.vals[i].isnumeric():
                    self.logger.info("String was not a valid numeric number.  Values are invalid.")
                    print("Invalid inputs: ", self.vals[i])
                    return False
                else:
                    self.vals[i] = int(self.vals[i])
            else:
                self.vals[i] = int(0)

        return True
    
    def check_size(self):
        self.horizontal_len, self.vertical_len = self.combine_vals()
        too_large = False
        message = ""

        if self.horizontal_len > config.MAX_HORIZONTAL and self.vertical_len > config.MAX_VERTICAL:
            message = (f"\nBoth cutss are too large:\n"
                        f"Horizontal: {self.horizontal_len} is greater than {config.MAX_HORIZONTAL}\n"
                        f"Vertical: {self.vertical_len} is greater than {config.MAX_VERTICAL}")
            too_large = True
        elif self.horizontal_len > config.MAX_HORIZONTAL:
            message = (f"\nHorizontal cut is too large:\n{self.horizontal_len} > {config.MAX_HORIZONTAL}")
            too_large = True
        elif self.vertical_len > config.MAX_VERTICAL:
            message = (f"\nVertical cut is too large:\n{self.vertical_len} > {config.MAX_VERTICAL}")
            too_large = True
        
        if too_large:
            self.logger.info(message)

        else:
            message = (f"\nHorizontal: {self.horizontal_len/12} ft ({self.horizontal_len} in)\n"
                       f"Vertical: {self.vertical_len/12} ft ({self.vertical_len} in)")
        
        print(message)
        messagebox.showwarning("Cut Size Warning", message)
            

    def combine_vals(self):
        hor_len = self.vals[0] * 12 + self.vals[1] + self.vals[2] * (1/16)
        ver_len = self.vals[3] * 12 + self.vals[4] + self.vals[5] * (1/16)

        return hor_len, ver_len
    
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

        #image = PhotoImage(file=r"C:\Users\nizni\University of St. Thomas\Archimedes - Code\Archimedes\images\delete.png")
        # add after text for image on image=image,
        self.delete = ttk.Button(self, text="D",  command=self.delete_text)
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
        else:
            self.switch_entry_back()

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

    def switch_entry_back(self):
        if self.active_entry == self.input_measures[0].feet:
            self.active_entry = self.input_measures[1].frac
        elif self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[0].feet
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[0].inch 
        elif self.active_entry == self.input_measures[1].feet:
            self.active_entry = self.input_measures[0].frac
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[1].feet
        else:
            self.active_entry = self.input_measures[1].inch 

        self.active_entry.focus_set()