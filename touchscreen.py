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
            submit = ttk.Button(self, text="Send Cut", command=self.send_cuts)
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
        self.continue_window.focus_force