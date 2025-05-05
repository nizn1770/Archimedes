import sys
import config
import motor
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox

class Application(tk.Tk):
    def __init__(self, logger):
        super().__init__()

        self.logger = logger
        self.logger.info("Initializing Archimedes")

        self.title("Archimedes")
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("Q", self.quit_program)

        # Initialize motors
        try:
            motor.init_motors()
            self.logger.info("Motors initialized")
        except Exception as e:
            self.logger.error(f"Motor initialization failed: {str(e)}")
            messagebox.showerror("Initialization Error", f"Failed to initialize motors: {str(e)}")
            sys.exit(1)

        self.cancel_flag = False
        self.loading_screen = self.create_loading_screen()
        self.loading_screen.deiconify()

        self.after(2000, self.initialize_ui)

    def create_loading_screen(self):
        loading_window = tk.Toplevel(self)
        loading_window.attributes("-topmost", True)
        loading_window.geometry("800x480")
        loading_window.title("Initializing Archimedes")

        loading_window.columnconfigure(0, weight=1)
        loading_window.rowconfigure(0, weight=1)
        loading_window.rowconfigure(1, weight=1)

        try:
            logo_image = PhotoImage(file=config.LOGO_IMAGE)
            logo_image_label = tk.Label(loading_window, image=logo_image)
            logo_image_label.image = logo_image
            logo_image_label.grid(row=0, column=0, sticky="nsew")
        except tk.TclError:
            self.logger.error("Failed to load logo image")
            logo_image_label = tk.Label(loading_window, text="Archimedes", font="Arial 24")
            logo_image_label.grid(row=0, column=0, sticky="nsew")

        loading_label = tk.Label(loading_window, text="Loading Archimedes...", font="Arial 24", anchor='center')
        loading_label.grid(row=1, column=0, sticky="nsew")

        return loading_window

    def initialize_ui(self):
        self.loading_screen.destroy()
        self.logger.info("Archimedes initialized")
        self.attributes("-fullscreen", True)
        self.message_var = tk.StringVar()
        self.measure_init()

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
    
    def quit_program(self, event=None):
        self.logger.info("Quitting program")
        self.cancel_flag = True
        motor.cleanup_motors()
        self.destroy()
        sys.exit(0)

    def cancel_cut(self):
        self.cancel_flag = True
        self.logger.info("Cut canceled by user")

    def update_message(self, message):
        self.message_var.set(message)

    def measure_init(self):
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
                self.show_cutting()
            else:
                title = "Cut Canceled"
                message = "The cut has been canceled."
                messagebox.showinfo(title, message)

        self.clear_entries()
        self.keyboard.reset_entry()


    def confirm_cuts(self):
        self.confirmation_window = tk.Toplevel(self)
        self.confirmation_window.attributes("-topmost", True)
        self.confirmation_window.attributes("-fullscreen", True)
        self.confirmation_window.title("Confirm")

        self.confirmation_window.columnconfigure(0, weight=1)
        self.confirmation_window.columnconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(0, weight=1)
        self.confirmation_window.rowconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(2, weight=1)

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

    def show_cutting(self):
        self.cancel_flag = False
        self.cutting_window = tk.Toplevel(self)
        self.cutting_window.attributes("-topmost", True)
        self.cutting_window.attributes("-fullscreen", True)
        self.cutting_window.title("Cutting")

        self.cutting_window.columnconfigure(0, weight=1)
        self.cutting_window.columnconfigure(1, weight=1)
        self.cutting_window.rowconfigure(0, weight=1)
        self.cutting_window.rowconfigure(1, weight=1)

        cutting_label = ttk.Label(self.cutting_window, text="Cutting in Progress", font="Arial 32", anchor="center")
        cutting_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        cancel_button = ttk.Button(self.cutting_window, text="Cancel Cut", command=self.cancel_cut)
        cancel_button.grid(row=1, column=0, columnspan=2, sticky="nsew")

        threading.Thread(target=self.cut, daemon=True).start()

    def cut(self):
        try:
            x_len, y_len = self.horizontal_len, self.vertical_len

            # Horizontal cut
            self.logger.info("Executing horizontal cut")
            motor.make_hor_cut(y_len)
            if self.cancel_flag:
                self.logger.info("Canceling after horizontal cut")
                motor.return_to_home_from_hor_cut(y_len)
                self.after(0, lambda: self.cutting_window.destroy())
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                return

            self.cutting_window.destroy()

            # Prompt for scrap removal
            scrap_event = threading.Event()
            def show_scrap_prompt():
                messagebox.showinfo("Remove Scrap", "Remove scrap piece of panel and press OK to continue...")
                scrap_event.set()
            self.after(0, show_scrap_prompt)
            scrap_event.wait()

            # Confirm continuation
            self.continue_response = None
            self.after(0, self.confirm_continue)
            continue_event = threading.Event()
            def wait_continue():
                self.wait_window(self.continue_window)
                continue_event.set()
            self.after(0, wait_continue)
            continue_event.wait()

            if not self.continue_response or self.cancel_flag:
                self.logger.info("Canceling after scrap removal")
                motor.return_to_home_from_hor_cut(y_len)
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                return

            # Show cutting screen for vertical cut
            self.cutting_window = tk.Toplevel(self)
            self.cutting_window.attributes("-topmost", True)
            self.cutting_window.attributes("-fullscreen", True)
            self.cutting_window.title("Cutting")

            self.cutting_window.columnconfigure(0, weight=1)
            self.cutting_window.columnconfigure(1, weight=1)
            self.cutting_window.rowconfigure(0, weight=1)
            self.cutting_window.rowconfigure(1, weight=1)

            cutting_label = ttk.Label(self.cutting_window, text="Cutting in Progress", font="Arial 32", anchor="center")
            cutting_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

            cancel_button = ttk.Button(self.cutting_window, text="Cancel Cut", command=self.cancel_cut)
            cancel_button.grid(row=1, column=0, columnspan=2, sticky="nsew")

            # Vertical cut
            self.logger.info("Executing vertical cut")
            motor.make_ver_cut(x_len, y_len)
            if self.cancel_flag:
                self.logger.info("Canceling after vertical cut")
                motor.return_to_home(x_len, y_len)
                self.after(0, lambda: self.cutting_window.destroy())
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                return

            # Return to home
            self.logger.info("Returning to home")
            motor.return_to_home(x_len, y_len)

            self.after(0, lambda: self.cutting_window.destroy())
            self.after(0, lambda: messagebox.showinfo("Cut Completed", "The cut has been completed successfully"))

        except Exception as e:
            self.logger.error(f"Cut error: {str(e)}")
            self.after(0, lambda: self.cutting_window.destroy())
            self.after(0, lambda: messagebox.showerror("Cut Error", f"An error occurred during cutting: {str(e)}"))
            motor.cleanup_motors()

    def confirm_continue(self):
        self.continue_window = tk.Toplevel(self)
        self.continue_window.attributes("-topmost", True)
        self.continue_window.attributes("-fullscreen", True)
        self.continue_window.title("Continue Cut")

        self.continue_window.columnconfigure(0, weight=1)
        self.continue_window.columnconfigure(1, weight=1)
        self.continue_window.rowconfigure(0, weight=1)
        self.continue_window.rowconfigure(1, weight=1)

        question_label = ttk.Label(self.continue_window, text="Continue with vertical cut?", font="Arial 32", anchor='center')
        question_label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        confirmation_button = ttk.Button(self.continue_window, text="Confirm", command=lambda: self.continue_result(True))
        confirmation_button.grid(row=1, column=0, sticky="nsew")

        cancelation_button = ttk.Button(self.continue_window, text="Cancel", command=lambda: self.continue_result(False))
        cancelation_button.grid(row=1, column=1, sticky="nsew")

    def continue_result(self, response):
        self.logger.info(f"Continue confirmation response: {response}")
        self.continue_response = response
        self.continue_window.destroy()

    def validate_inputs(self):
        self.valid_inputs = False
        self.get_vals()
        self.check_numeric()
        self.check_size()

        if self.numeric and not self.bad_cut_length:
            self.valid_inputs = True
        else:
            self.valid_inputs = False

    def get_vals(self):
        self.vals = [self.hor.inch.get(), self.hor.frac.get(),
                     self.vert.inch.get(), self.vert.frac.get()]

    def check_numeric(self):
        self.numeric = True
        for i in range(0, 4):
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
                       f"Max Vertical Cut: {config.MAX_VERTICAL} in\n"
                       f"Input Vertical Cut: {self.vertical_len} in\n")
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

        self.title = ttk.Label(self, text=title_text, font=('Arial', 16))
        self.title.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.inch = ttk.Entry(self, font=('Arial', 12))
        self.inch.grid(row=1, column=0, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", font=('Arial', 12))
        self.inch_label.grid(row=2, column=0, sticky="n")

        self.frac = ttk.Entry(self, font=('Arial', 12))
        self.frac.grid(row=1, column=1, sticky="ew")

        self.frac_label = ttk.Label(self, text="1/8 inch", font=('Arial', 12))
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

        try:
            self.checkmark_image = PhotoImage(file=config.NEXT_IMAGE)
            self.next = ttk.Button(self, text="Next", image=self.checkmark_image, command=self.switch_entry)
        except tk.TclError:
            self.logger.error("Failed to load checkmark image")
            self.next = ttk.Button(self, text="Next", command=self.switch_entry)
        self.next.grid(row=3, column=0, sticky="nsew")

        self.zero = ttk.Button(self, text="0", command=lambda: self.insert_text(0))
        self.zero.grid(row=3, column=1, sticky="nsew")

        try:
            self.delete_image = PhotoImage(file=config.DELETE_IMAGE)
            self.delete = ttk.Button(self, text="Delete", image=self.delete_image, command=self.delete_text)
        except tk.TclError:
            self.logger.error("Failed to load delete image")
            self.delete = ttk.Button(self, text="Delete", command=self.delete_text)
        self.delete.grid(row=3, column=2, sticky="nsew")
        
    def insert_text(self, char):
        if self.active_entry:
            self.active_entry.insert(tk.END, str(char))
            self.active_entry.focus_set()

    def delete_text(self):
        current_text = self.active_entry.get()
        if current_text:
            self.active_entry.delete(len(current_text)-1, tk.END)
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