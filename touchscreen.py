import sys
import config
import requests
import threading
import time
import progress_window
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from io import BytesIO
import test



class Application(tk.Tk):
    def __init__(self, logger):
        super().__init__()

        self.logger = logger
        self.logger.info("Archimedes initialized")

        self.vals = [0,0,0,0]

        self.message_var = tk.StringVar(value="test")
        self.cut_title = "test"
        self.cut_message = "test"
        
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
        self.hor.inch.focus_set()

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

    def update_message(self, message):
        self.message_var.set(message)


    def send_cuts(self):
        self.validate_inputs()
        if self.valid_inputs:
            message = (f"Horizontal: {self.make_hor_printout()} in\n"
                       f"Vertical: {self.make_ver_printout()} in")
            self.update_message(message)

            self.confirmation_response = None
            self.confirm_cuts()

            self.wait_window(self.confirmation_window)

            if self.confirmation_response:
                self.show_progress()
                self.wait_window(self.progress_window)
                messagebox.showinfo(self.cut_title, self.cut_message)
                
            else:
                title = "Cut Canceled"
                message = "The cut has been canceled."
                messagebox.showinfo(title, message)

        self.clear_entries()
        self.keyboard.reset_entry()

        #messagebox.showinfo("Returning to Home", "Returning Cut Head to Home.  Wait to retrieve and load")

    def confirm_cuts(self):
        self.confirmation_window = tk.Toplevel(self)
        self.confirmation_window.attributes("-topmost", True)
        self.confirmation_window.attributes("-fullscreen", True)
        self.confirmation_window.title("Confirm")

        self.confirmation_window.columnconfigure(0, weight=1)
        self.confirmation_window.columnconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(0, weight=1)
        self.confirmation_window.rowconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(2, weight=3)

        question_label = ttk.Label(self.confirmation_window, text="Is this the correct cut?", font="Arial 32", anchor='center')
        question_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        cut_length = ttk.Label(self.confirmation_window, textvariable=self.message_var, font="Arial 24", anchor='center')
        cut_length.grid(row=1, column=0, columnspan=2, sticky="nsew")

        confirmation_button = ttk.Button(self.confirmation_window, text="Confirm", command=lambda: self.confirmation_result(True))
        confirmation_button.grid(row=2, column=0, sticky="nsew")

        cancelation_button = ttk.Button(self.confirmation_window, text="Cancel", command=lambda: self.confirmation_result(False))
        cancelation_button.grid(row=2, column=1, sticky="nsew")


    def confirmation_result(self, response):
        self.logger.info(f"Cut confirmation response: {response}")
        self.confirmation_response = response
        self.confirmation_window.destroy()


    def show_progress(self):        
        self.cancel_flag = False

        self.progress_window = tk.Toplevel(self)
        self.progress_window.attributes("-topmost", True)
        self.progress_window.attributes("-fullscreen", True)
        self.progress_window.title("Cutting")

        self.progress_window.columnconfigure(0, weight=1)

        self.progress_window.rowconfigure(0, weight=1)
        self.progress_window.rowconfigure(1, weight=1)
        self.progress_window.rowconfigure(2, weight=1)
        self.progress_window.rowconfigure(3, weight=3)

        progress_label = ttk.Label(self.progress_window, text="Cutting Board", font="Arial 32", anchor="center")
        progress_label.grid(row=0, column=0, sticky="nsew")

        cut_length = ttk.Label(self.progress_window, textvariable=self.message_var, font="Arial 24", anchor="center")
        cut_length.grid(row=1, column=0, sticky="nsew")

        self.progress_bar = ttk.Progressbar(self.progress_window, maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky="nsew")

        cancel_button = ttk.Button(self.progress_window, text="Cancel Cut", command=lambda: self.cancel_process())
        cancel_button.grid(row=3, column=0, sticky="nsew")

        self.begin_progress()


    def begin_progress(self):
        self.cancel_flag = False
        self.progress_bar["value"]=0
        threading.Thread(target=self.cut).start()
        threading.Thread(target=test.rotate_motor, args=(self.vals[0]+self.vals[1]*(1/8))).start()

        self.logger.info("Starting Cut") 

    def cut(self):
        try:
            for i in range(int(self.vals[0]+self.vals[1]*(1/8)*(1/test.SLEEP_TIME))):
                if self.cancel_flag:
                    self.cut_title = "Cut Canceled"
                    self.cut_message = "The cut has been canceled without completing."
                    break
                else:
                    self.progress_bar.step(2)
                time.sleep(test.SLEEP_TIME)
            if not self.cancel_flag:
                self.cut_title = "Cut Completed"
                self.cut_message = "The cut has been completed successfully"
            self.logger.info(f"{self.cut_title} - {self.cut_message}")
            print("done")
            self.progress_window.destroy()
        except Exception as e:
            print(f"Error in cut(): {e}")


    def cancel_process(self):
        self.cancel_flag = True
  
     
        
    def validate_inputs(self):
        self.valid_inputs = False
        self.get_vals()
        self.check_numeric()
        self.check_size()

        if self.numeric and not self.bad_cut_length:
            self.valid_inputs = True
        else:
            self.valid_inputs =  False


    def get_vals(self):
        self.vals = [self.hor.inch.get(), self.hor.frac.get(),
        self.vert.inch.get(), self.vert.frac.get()]


    def check_numeric(self):
        self.numeric = True
        for i in range(0,4):
            if self.vals[i]:
                if not self.vals[i].isnumeric():
                    self.logger.info(f"Invalid value: {self.vals[i]}")
                    self.numeric = False
                else:
                    self.vals[i] = int(self.vals[i])
            else:
                self.vals[i] = int(0)

    
    def check_size(self):
        self.horizontal_len, self.vertical_len = self.combine_vals()
        self.bad_cut_length = False
        message = ""

        if self.horizontal_len > config.MAX_HORIZONTAL:
            message += (f"\nHorizontal cut is too large:\n"
                       f"Max Horizontal Cut: {config.MAX_HORIZONTAL} in\n"
                       f"Input Horizontal Cut: {self.horizontal_len} in\n")
            self.bad_cut_length = True
        
        if self.horizontal_len < config.MIN_HORIZONTAL:
            message += (f"\nHorizontal cut is too small:\n"
                       f"Min Horizontal Cut: {config.MIN_HORIZONTAL} in\n"
                       f"Input Horizontal Cut: {self.horizontal_len} in\n")
            self.bad_cut_length = True

        if self.vertical_len > config.MAX_VERTICAL:
            message += (f"\nVertical cut is too large:\n"
                       f"Max Vertical Cut: {config.MAX_VERTICAL} in)\n"
                       f"Input Vertical Cut: {self.vertical_len} in)\n")
            self.bad_cut_length = True
                
        if self.vertical_len < config.MIN_VERTICAL:
            message += (f"\nVertical cut is too small:\n"
                       f"Min Vertical Cut: {config.MIN_VERTICAL} in\n"
                       f"Input Vertical Cut: {self.vertical_len} in\n")
            self.bad_cut_length = True

        if self.bad_cut_length:
            messagebox.showwarning("Cut Size Warning", message)

        else:
            message = (f"Horizontal: {self.horizontal_len} in, Vertical: {self.vertical_len} in")
        
        self.logger.info(message)
        print(message)
            


    def make_hor_printout(self):
        hor_len = f"{self.vals[0]} {self.vals[1]}/8"

        return hor_len
    
    def make_ver_printout(self):
        ver_len = f"{self.vals[2]} {self.vals[3]}/8"

        return ver_len
    

    def combine_vals(self):
        hor_len = self.vals[0] + self.vals[1] * (1/8)
        ver_len = self.vals[2] + self.vals[3] * (1/8)

        return hor_len, ver_len
    

    def clear_entries(self):
        for input_measure in [self.hor, self.vert]:
            input_measure.inch.delete(0, tk.END)
            input_measure.frac.delete(0, tk.END)

class InputMeasure(ttk.Frame):
    def __init__(self, parent, title_text):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.title = ttk.Label(self, text=title_text, font=('Arial 16'))
        self.title.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.inch = ttk.Entry(self, font=('Arial 12'))
        self.inch.grid(row=1, column=0, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", font=('Arial 12'))
        self.inch_label.grid(row=2, column=0, sticky="n")

        self.frac = ttk.Entry(self, font=('Arial 12'))
        self.frac.grid(row=1, column=1, sticky="ew")

        self.frac_label = ttk.Label(self, text="1/8 inch", font=('Arial 12'))
        self.frac_label.grid(row=2, column=1, sticky="n")

class KeyBoard(ttk.Frame):
    def __init__(self, parent, input_measures):
        super().__init__(parent)
        
        self.input_measures = input_measures
        self.active_entry = input_measures[0].inch

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

        self.checkmark_image = self.download_image(config.NEXT_IMAGE)
        self.next = ttk.Button(self, text="N", image=self.checkmark_image, command=self.switch_entry)
        self.next.grid(row=3, column=0, sticky="nsew")

        self.zero = ttk.Button(self, text="0", command=lambda: self.insert_text(0))
        self.zero.grid(row=3, column=1, sticky="nsew")

        self.delete_image = self.download_image(config.DELETE_IMAGE)
        self.delete = ttk.Button(self, text="D", image=self.delete_image,  command=self.delete_text)
        self.delete.grid(row=3, column=2, sticky="nsew")
        
    def download_image(self, image_url):
        response = requests.get(image_url)
        image_data = response.content
        return PhotoImage(data=image_data)

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
        self.active_entry = self.input_measures[0].inch
        self.active_entry.focus_set()

    def switch_entry(self):
        if self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[0].frac
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[1].inch
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[1].frac
        else:
            self.active_entry = self.input_measures[0].inch  

        self.active_entry.focus_set()

    def switch_entry_back(self):
        if self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[1].frac
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[0].inch 
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[0].frac
        else:
            self.active_entry = self.input_measures[1].inch 

        self.active_entry.focus_set()