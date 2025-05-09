import sys
import config
import cnc_motor as motor
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
import requests
import os

class Application(tk.Tk):
    def __init__(self, logger):
        super().__init__()

        self.logger = logger
        self.logger.info("Initializing Archimedes")
        self.logger.info(f"Imported motor module from: {motor.__file__}")
        self.logger.info(f"Screen resolution: {self.winfo_screenwidth()}x{self.winfo_screenheight()}")

        self.title("Archimedes")
        self.bind("<Escape>", self.exit_fullscreen)
        self.bind("Q", self.quit_program)

        # Hide main window during initialization
        self.withdraw()
        self.logger.debug("Main window hidden during initialization")

        # Initialize motors
        try:
            motor.init_motors()
            self.logger.info("Motors initialized")
        except Exception as e:
            self.logger.error(f"Motor initialization failed: {str(e)}")
            messagebox.showerror("Initialization Error", f"Failed to initialize motors: {str(e)}")
            sys.exit(1)

        self.cancel_flag = False
        self.horizontal_len = 0
        self.vertical_len = 0
        self.loading_screen = self.create_loading_screen()
        self.loading_screen.deiconify()

        self.after(2000, self.initialize_ui)

    def create_loading_screen(self):
        self.logger.info("Creating loading screen")
        loading_window = tk.Toplevel(self)
        loading_window.attributes("-topmost", True)
        try:
            loading_window.attributes("-fullscreen", True)
            self.logger.debug("Loading window set to fullscreen")
        except tk.TclError:
            self.logger.warning("Fullscreen failed for loading window, setting fixed geometry")
            loading_window.geometry("800x480")
        loading_window.title("Initializing Archimedes")
        loading_window.focus_force()
        self.logger.debug(f"Loading window created: {loading_window.winfo_geometry()}")

        loading_window.columnconfigure(0, weight=1)
        loading_window.rowconfigure(0, weight=1)
        loading_window.rowconfigure(1, weight=1)

        # Try to load cached image first
        cached_image_path = "images/logo_cached.png"
        logo_image = None
        if os.path.exists(cached_image_path):
            try:
                logo_image = PhotoImage(file=cached_image_path)
                self.logger.debug("Loaded cached logo image")
            except tk.TclError as e:
                self.logger.error(f"Failed to load cached logo image: {str(e)}")

        # Attempt to download image if no valid cached image
        if not logo_image:
            logo_image = self.download_image(config.LOGO_IMAGE)
            if logo_image:
                # Cache the downloaded image
                try:
                    os.makedirs("images", exist_ok=True)
                    with open(cached_image_path, "wb") as f:
                        response = requests.get(config.LOGO_IMAGE, timeout=5)
                        f.write(response.content)
                    self.logger.debug("Cached downloaded logo image")
                except Exception as e:
                    self.logger.error(f"Failed to cache logo image: {str(e)}")

        try:
            if logo_image:
                logo_image_label = tk.Label(loading_window, image=logo_image)
                logo_image_label.image = logo_image  # Keep reference
                logo_image_label.grid(row=0, column=0, sticky="nsew")
                self.logger.debug("Logo image gridded")
            else:
                raise tk.TclError("No valid logo image available")
        except tk.TclError as e:
            self.logger.error(f"Failed to display logo image: {str(e)}")
            logo_image_label = tk.Label(loading_window, text="Archimedes", font="Arial 24", anchor="center")
            logo_image_label.grid(row=0, column=0, sticky="nsew")
            self.logger.debug("Fallback text label gridded")

        loading_label = tk.Label(loading_window, text="Loading Archimedes...", font="Arial 24", anchor="center")
        loading_label.grid(row=1, column=0, sticky="nsew")
        self.logger.debug("Loading screen label added")

        loading_window.update()
        self.logger.debug("Loading window updated")

        return loading_window

    def download_image(self, image_url):
        try:
            response = requests.get(image_url, timeout=5)
            response.raise_for_status()
            image_data = response.content
            return PhotoImage(data=image_data)
        except (requests.exceptions.RequestException, tk.TclError) as e:
            self.logger.error(f"Failed to download image from {image_url}: {str(e)}")
            return None

    def initialize_ui(self):
        self.loading_screen.destroy()
        self.logger.info("Loading screen destroyed")
        self.deiconify()
        self.logger.debug("Main window shown")
        try:
            self.attributes("-fullscreen", True)
            self.logger.info("Set to fullscreen mode")
        except tk.TclError:
            self.logger.warning("Fullscreen mode failed, setting fixed geometry")
            self.geometry("800x480")
        self.message_var = tk.StringVar()
        try:
            self.measure_init()
        except Exception as e:
            self.logger.error(f"Failed to initialize measurement UI: {str(e)}")
            messagebox.showerror("UI Error", f"Failed to initialize UI: {str(e)}")
        self.update()
        self.logger.info(f"Main window geometry: {self.winfo_geometry()}")

    def exit_fullscreen(self, event=None):
        self.logger.info("Exiting fullscreen mode")
        self.attributes("-fullscreen", False)
        self.geometry("800x480")

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
        self.logger.debug(f"Updating message: {message}")
        self.message_var.set(message)

    def measure_init(self):
        self.logger.info("Initializing measurement UI")
        self.columnconfigure(0, weight=1, minsize=300)
        self.columnconfigure(1, weight=1, minsize=300)
        self.rowconfigure(0, weight=1, minsize=100)
        self.rowconfigure(1, weight=1, minsize=100)
        self.rowconfigure(2, weight=2, minsize=150)

        try:
            self.hor = InputMeasure(self, "Horizontal")
            self.hor.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.hor.inch.focus_set()
            self.logger.debug(f"Horizontal InputMeasure created and gridded: {self.hor.winfo_geometry()}")
        except Exception as e:
            self.logger.error(f"Failed to create Horizontal InputMeasure: {str(e)}")
            raise

        try:
            self.vert = InputMeasure(self, "Vertical")
            self.vert.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.logger.debug(f"Vertical InputMeasure created and gridded: {self.vert.winfo_geometry()}")
        except Exception as e:
            self.logger.error(f"Failed to create Vertical InputMeasure: {str(e)}")
            raise

        try:
            submit = ttk.Button(self, text="Send Cut") #command=self.send_cuts
            submit.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
            self.logger.debug(f"Submit button created and gridded: {submit.winfo_geometry()}")
        except Exception as e:
            self.logger.error(f"Failed to create Submit button: {str(e)}")
            raise

        try:
            self.keyboard = KeyBoard(self, [self.hor, self.vert], self.logger)
            self.keyboard.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=5, pady=5)
            self.logger.info(f"Keyboard widget created and gridded: {self.keyboard.winfo_geometry()}")
        except Exception as e:
            self.logger.error(f"Failed to create KeyBoard: {str(e)}")
            raise

        self.update()

        try:
            threading.Thread(target=motor.design_show, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Failed to start design_show thread: {str(e)}")


    def send_cuts(self):
        self.logger.info("Processing send_cuts")
        self.validate_inputs()
        if self.valid_inputs and self.horizontal_len >= config.MIN_HORIZONTAL and self.vertical_len >= config.MIN_VERTICAL:
            message = (f"Horizontal: {self.make_hor_printout()} in\n"
                       f"Vertical: {self.make_ver_printout()} in")
            self.update_message(message)

            self.confirmation_response = None
            self.confirm_cuts()

            self.wait_window(self.confirmation_window)

            if self.confirmation_response:
                self.logger.info(f"Starting cut with horizontal_len={self.horizontal_len}, vertical_len={self.vertical_len}")
                self.show_cutting()
            else:
                title = "Cut Canceled"
                message = "The cut has been canceled."
                self.logger.info("Cut canceled during confirmation")
                messagebox.showinfo(title, message)
        else:
            self.logger.error(f"Validation failed: valid_inputs={self.valid_inputs}, horizontal_len={self.horizontal_len}, vertical_len={self.vertical_len}")
            messagebox.showerror("Validation Error", "Invalid input values. Please enter valid numeric values within the allowed range.")

        self.clear_entries()
        self.keyboard.reset_entry()

    def confirm_cuts(self):
        self.logger.info("Showing cut confirmation window")
        self.withdraw()
        self.confirmation_window = tk.Toplevel(self)
        self.confirmation_window.attributes("-topmost", True)
        try:
            self.confirmation_window.attributes("-fullscreen", True)
            self.logger.debug("Confirmation window set to fullscreen")
        except tk.TclError:
            self.logger.warning("Fullscreen failed for confirmation window, setting fixed geometry")
            self.confirmation_window.geometry("800x480")
        self.confirmation_window.title("Confirm")
        self.confirmation_window.focus_force()
        self.logger.debug(f"Confirmation window created: {self.confirmation_window.winfo_geometry()}")

        self.confirmation_window.columnconfigure(0, weight=1)
        self.confirmation_window.columnconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(0, weight=1)
        self.confirmation_window.rowconfigure(1, weight=1)
        self.confirmation_window.rowconfigure(2, weight=1)

        question_label = ttk.Label(self.confirmation_window, text="Is this the correct cut?", font="Arial 32", anchor='center')
        question_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logger.debug("Confirmation question label added")

        cut_length = ttk.Label(self.confirmation_window, textvariable=self.message_var, font="Arial 24", anchor='center')
        cut_length.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.logger.debug("Cut length label added")

        confirmation_button = ttk.Button(self.confirmation_window, text="Confirm", command=lambda: self.confirmation_result(True))
        confirmation_button.grid(row=2, column=0, sticky="nsew")
        self.logger.debug("Confirmation button added")

        cancelation_button = ttk.Button(self.confirmation_window, text="Cancel", command=lambda: self.confirmation_result(False))
        cancelation_button.grid(row=2, column=1, sticky="nsew")
        self.logger.debug("Cancelation button added")

    def confirmation_result(self, response):
        self.logger.info(f"Cut confirmation response: {response}")
        self.confirmation_response = response
        self.confirmation_window.destroy()
        if not response:
            self.deiconify()

    def show_cutting(self):
        self.cancel_flag = False
        self.logger.info("Showing cutting screen")
        self.withdraw()
        self.cutting_window = tk.Toplevel(self)
        self.cutting_window.attributes("-topmost", True)
        try:
            self.cutting_window.attributes("-fullscreen", True)
            self.logger.debug("Cutting window set to fullscreen")
        except tk.TclError:
            self.logger.warning("Fullscreen failed for cutting window, setting fixed geometry")
            self.cutting_window.geometry("800x480")
        self.cutting_window.title("Cutting")
        self.cutting_window.focus_force()
        self.logger.debug(f"Cutting window created: {self.cutting_window.winfo_geometry()}")

        self.cutting_window.columnconfigure(0, weight=1)
        self.cutting_window.columnconfigure(1, weight=1)
        self.cutting_window.rowconfigure(0, weight=1)
        self.cutting_window.rowconfigure(1, weight=1)

        cutting_label = ttk.Label(self.cutting_window, text="Cutting in Progress", font="Arial 32", anchor="center")
        cutting_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logger.debug("Cutting in progress label added")

        cancel_button = ttk.Button(self.cutting_window, text="Cancel Cut", command=self.cancel_cut)
        cancel_button.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.logger.debug("Cancel cut button added")

        threading.Thread(target=self.cut, daemon=True).start()

    def cut(self):
        try:
            x_len, y_len = self.horizontal_len, self.vertical_len
            self.logger.info(f"Cut started with x_len={x_len}, y_len={y_len}")

            # Horizontal cut
            self.logger.info("Executing horizontal cut")
            motor.make_hor_cut(y_len)
            if self.cancel_flag:
                self.logger.info("Canceling after horizontal cut")
                motor.return_to_home_from_hor_cut(y_len)
                self.after(0, lambda: self.cutting_window.destroy())
                self.after(0, lambda: self.deiconify())
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                self.after(0, lambda: messagebox.showinfo("Returning to Home", "Returning Cut Head to Home. Wait to retrieve and load"))
                return

            self.cutting_window.destroy()
            self.logger.debug("Closed cutting window after horizontal cut")

            # Prompt for scrap removal
            scrap_event = threading.Event()
            def show_scrap_prompt():
                self.logger.info("Showing scrap removal prompt")
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
                self.after(0, lambda: self.deiconify())
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                self.after(0, lambda: messagebox.showinfo("Returning to Home", "Returning Cut Head to Home. Wait to retrieve and load"))
                return

            # Show cutting screen for vertical cut
            self.cutting_window = tk.Toplevel(self)
            self.cutting_window.attributes("-topmost", True)
            try:
                self.cutting_window.attributes("-fullscreen", True)
                self.logger.debug("Cutting window set to fullscreen for vertical cut")
            except tk.TclError:
                self.logger.warning("Fullscreen failed for cutting window, setting fixed geometry")
                self.cutting_window.geometry("800x480")
            self.cutting_window.title("Cutting")
            self.cutting_window.focus_force()
            self.logger.debug(f"Cutting window created for vertical cut: {self.cutting_window.winfo_geometry()}")

            self.cutting_window.columnconfigure(0, weight=1)
            self.cutting_window.columnconfigure(1, weight=1)
            self.cutting_window.rowconfigure(0, weight=1)
            self.cutting_window.rowconfigure(1, weight=1)

            cutting_label = ttk.Label(self.cutting_window, text="Cutting in Progress", font="Arial 32", anchor="center")
            cutting_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
            self.logger.debug("Cutting in progress label added for vertical cut")

            cancel_button = ttk.Button(self.cutting_window, text="Cancel Cut", command=self.cancel_cut)
            cancel_button.grid(row=1, column=0, columnspan=2, sticky="nsew")
            self.logger.debug("Cancel cut button added for vertical cut")

            # Vertical cut
            self.logger.info("Executing vertical cut")
            motor.make_ver_cut(x_len, y_len)
            if self.cancel_flag:
                self.logger.info("Canceling after vertical cut")
                motor.return_to_home(x_len, y_len)
                self.after(0, lambda: self.cutting_window.destroy())
                self.after(0, lambda: self.deiconify())
                self.after(0, lambda: messagebox.showinfo("Cut Canceled", "The cut was canceled. Machine returned to home."))
                self.after(0, lambda: messagebox.showinfo("Returning to Home", "Returning Cut Head to Home. Wait to retrieve and load"))
                return

            # Return to home
            self.logger.info("Returning to home")
            motor.return_to_home(x_len, y_len)

            self.after(0, lambda: self.cutting_window.destroy())
            self.after(0, lambda: self.deiconify())
            self.after(0, lambda: messagebox.showinfo("Cut Completed", "The cut has been completed successfully"))
            self.after(0, lambda: messagebox.showinfo("Returning to Home", "Returning Cut Head to Home. Wait to retrieve and load"))
            self.logger.info("Cut completed successfully")

        except Exception as e:
            error_msg = f"Cut error: {str(e)}"
            self.logger.error(error_msg)
            self.after(0, lambda msg=error_msg: self.cutting_window.destroy())
            self.after(0, lambda msg=error_msg: self.deiconify())
            self.after(0, lambda msg=error_msg: messagebox.showerror("Cut Error", f"An error occurred during cutting: {msg}"))
            self.after(0, lambda: messagebox.showinfo("Returning to Home", "Returning Cut Head to Home. Wait to retrieve and load"))
            motor.cleanup_motors()

    def confirm_continue(self):
        self.logger.info("Showing continue confirmation window")
        self.withdraw()
        self.continue_window = tk.Toplevel(self)
        self.continue_window.attributes("-topmost", True)
        try:
            self.continue_window.attributes("-fullscreen", True)
            self.logger.debug("Continue window set to fullscreen")
        except tk.TclError:
            self.logger.warning("Fullscreen failed for continue window, setting fixed geometry")
            self.continue_window.geometry("800x480")
        self.continue_window.title("Continue Cut")
        self.continue_window.focus_force()
        self.logger.debug(f"Continue window created: {self.continue_window.winfo_geometry()}")

        self.continue_window.columnconfigure(0, weight=1)
        self.continue_window.columnconfigure(1, weight=1)
        self.continue_window.rowconfigure(0, weight=1)
        self.continue_window.rowconfigure(1, weight=1)

        question_label = ttk.Label(self.continue_window, text="Continue with vertical cut?", font="Arial 32", anchor='center')
        question_label.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logger.debug("Continue question label added")

        confirmation_button = ttk.Button(self.continue_window, text="Confirm", command=lambda: self.continue_result(True))
        confirmation_button.grid(row=1, column=0, sticky="nsew")
        self.logger.debug("Continue confirmation button added")

        cancelation_button = ttk.Button(self.continue_window, text="Cancel", command=lambda: self.continue_result(False))
        cancelation_button.grid(row=1, column=1, sticky="nsew")
        self.logger.debug("Continue cancelation button added")

    def continue_result(self, response):
        self.logger.info(f"Continue confirmation response: {response}")
        self.continue_response = response
        self.continue_window.destroy()

    def validate_inputs(self):
        self.logger.info("Validating inputs")
        self.valid_inputs = False
        self.get_vals()
        self.check_numeric()
        self.check_size()
        self.logger.info(f"Validation result: valid_inputs={self.valid_inputs}, horizontal_len={self.horizontal_len}, vertical_len={self.vertical_len}")

        if self.numeric and not self.bad_cut_length:
            self.valid_inputs = True
        else:
            self.valid_inputs = False
            self.logger.warning("Validation failed due to numeric or size constraints")

    def get_vals(self):
        raw_vals = [self.hor.inch.get(), self.hor.frac.get(),
                    self.vert.inch.get(), self.vert.frac.get()]
        self.logger.info(f"Raw input values: {raw_vals}")
        self.vals = []
        for val in raw_vals:
            if not val:
                self.vals.append(0)
            else:
                self.vals.append(val)

    def check_numeric(self):
        self.logger.info("Checking numeric input")
        self.numeric = True
        for i in range(0, 4):
            if self.vals[i] != 0:
                if not str(self.vals[i]).isnumeric():
                    self.logger.info(f"Invalid value: {self.vals[i]}")
                    self.numeric = False
                    self.vals[i] = 0
                else:
                    self.vals[i] = int(self.vals[i])
            else:
                self.vals[i] = 0
        self.logger.info(f"Processed numeric values: {self.vals}")

    def check_size(self):
        self.logger.info("Checking input size constraints")
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
            self.logger.warning(f"Size validation failed: {message}")
            messagebox.showwarning("Cut Size Warning", message)
        else:
            message = (f"Horizontal: {self.horizontal_len} in, Vertical: {self.vertical_len} in")
            self.logger.info(message)

    def make_hor_printout(self):
        hor_len = f"{self.vals[0]} {self.vals[1]}/8"
        self.logger.debug(f"Horizontal printout: {hor_len}")
        return hor_len
    
    def make_ver_printout(self):
        ver_len = f"{self.vals[2]} {self.vals[3]}/8"
        self.logger.debug(f"Vertical printout: {ver_len}")
        return ver_len
    
    def combine_vals(self):
        self.logger.info(f"Combining values: {self.vals}")
        try:
            hor_len = self.vals[0] + self.vals[1] * (1/8)
            ver_len = self.vals[2] + self.vals[3] * (1/8)
        except TypeError as e:
            self.logger.error(f"Error combining values: {str(e)}, vals={self.vals}")
            hor_len = 0
            ver_len = 0
        self.logger.debug(f"Combined values: horizontal_len={hor_len}, vertical_len={ver_len}")
        return hor_len, ver_len
    
    def clear_entries(self):
        self.logger.info("Clearing input entries")
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

        self.title = ttk.Label(self, text=title_text, font=('Arial', 24))
        self.title.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.inch = ttk.Entry(self, font=('Arial', 16))
        self.inch.grid(row=1, column=0, sticky="ew")

        self.inch_label = ttk.Label(self, text="Inches", font=('Arial', 16))
        self.inch_label.grid(row=2, column=0, sticky="n")

        self.frac = ttk.Entry(self, font=('Arial', 12))
        self.frac.grid(row=1, column=1, sticky="ew")

        self.frac_label = ttk.Label(self, text="1/8 inch", font=('Arial', 16))
        self.frac_label.grid(row=2, column=1, sticky="n")

class KeyBoard(ttk.Frame):
    def __init__(self, parent, input_measures, logger):
        super().__init__(parent)
        self.logger = logger
        self.logger.info("Initializing KeyBoard")
        
        self.input_measures = input_measures
        self.active_entry = input_measures[0].inch if input_measures else None
        self.logger.debug(f"Initial active entry: {self.active_entry}")

        self.columnconfigure(0, weight=1, minsize=80)
        self.columnconfigure(1, weight=1, minsize=80)
        self.columnconfigure(2, weight=1, minsize=80)
        self.rowconfigure(0, weight=1, minsize=60)
        self.rowconfigure(1, weight=1, minsize=60)
        self.rowconfigure(2, weight=1, minsize=60)
        self.rowconfigure(3, weight=1, minsize=60)

        self.one = ttk.Button(self, text="1", command=lambda: self.insert_text(1), width=8)
        self.one.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.two = ttk.Button(self, text="2", command=lambda: self.insert_text(2), width=8)
        self.two.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.three = ttk.Button(self, text="3", command=lambda: self.insert_text(3), width=8)
        self.three.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        self.four = ttk.Button(self, text="4", command=lambda: self.insert_text(4), width=8)
        self.four.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.five = ttk.Button(self, text="5", command=lambda: self.insert_text(5), width=8)
        self.five.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.six = ttk.Button(self, text="6", command=lambda: self.insert_text(6), width=8)
        self.six.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        self.seven = ttk.Button(self, text="7", command=lambda: self.insert_text(7), width=8)
        self.seven.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        self.eight = ttk.Button(self, text="8", command=lambda: self.insert_text(8), width=8)
        self.eight.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        self.nine = ttk.Button(self, text="9", command=lambda: self.insert_text(9), width=8)
        self.nine.grid(row=2, column=2, sticky="nsew", padx=5, pady=5)

        self.checkmark_image = self.download_image(config.NEXT_IMAGE)
        self.next = ttk.Button(self, image=self.checkmark_image, command=self.switch_entry, width=8)
        self.next.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        if not self.checkmark_image:
            self.next.configure(text="Next")
            self.logger.debug("Fallback to text for Next button")

        self.zero = ttk.Button(self, text="0", command=lambda: self.insert_text(0), width=8)
        self.zero.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        self.delete_image = self.download_image(config.DELETE_IMAGE)
        self.delete = ttk.Button(self, image=self.delete_image, command=self.delete_text, width=8)
        self.delete.grid(row=3, column=2, sticky="nsew", padx=5, pady=5)
        if not self.delete_image:
            self.delete.configure(text="Del")
            self.logger.debug("Fallback to text for Delete button")
        
        self.logger.info("Keyboard buttons initialized")
        self.logger.debug(f"Keyboard geometry: {self.winfo_geometry()}")

    def download_image(self, image_url):
        response = requests.get(image_url)
        image_data = response.content
        return PhotoImage(data=image_data)

    def insert_text(self, char):
        if self.active_entry:
            self.active_entry.insert(tk.END, str(char))
            self.active_entry.focus_set()
            self.logger.info(f"Inserted {char} into {self.active_entry}")

    def delete_text(self):
        if self.active_entry:
            current_text = self.active_entry.get()
            if current_text:
                self.active_entry.delete(len(current_text)-1, tk.END)
                self.logger.info(f"Deleted character from {self.active_entry}")
            else:
                self.switch_entry_back()
                self.logger.info(f"Switched back entry due to empty field")

    def reset_entry(self):
        self.active_entry = self.input_measures[0].inch if self.input_measures else None
        self.logger.info(f"Reset active entry to {self.active_entry}")
        if self.active_entry:
            self.active_entry.focus_set()

    def switch_entry(self):
        if not self.active_entry or not self.input_measures:
            self.logger.warning("No active entry or input measures for switch_entry")
            return
        if self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[0].frac
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[1].inch
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[1].frac
        else:
            self.active_entry = self.input_measures[0].inch
        self.active_entry.focus_set()
        self.logger.info(f"Switched to active entry: {self.active_entry}")

    def switch_entry_back(self):
        if not self.active_entry or not self.input_measures:
            self.logger.warning("No active entry or input measures for switch_entry_back")
            return
        if self.active_entry == self.input_measures[0].inch:
            self.active_entry = self.input_measures[1].frac
        elif self.active_entry == self.input_measures[0].frac:
            self.active_entry = self.input_measures[0].inch
        elif self.active_entry == self.input_measures[1].inch:
            self.active_entry = self.input_measures[0].frac
        else:
            self.active_entry = self.input_measures[1].inch
        self.active_entry.focus_set()
        self.logger.info(f"Switched back to active entry: {self.active_entry}")