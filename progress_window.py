import sys
import config
import requests
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from io import BytesIO

class ProgressWindow:
    def __init__(self, parent, logger, message, screen_size):
        super().__init__(parent)
        self.logger = logger
        self.message = message
        self.screen_size = screen_size
        
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

        cut_length = ttk.Label(self.progress_window, text=self.message, font="Arial 24", anchor="center")
        cut_length.grid(row=1, column=0, sticky="nsew")

        self.progress_bar = ttk.Progressbar(self.progress_window, maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky="nsew")

        cancel_button = ttk.Button(self.progress_window, text="Cancel Cut", command=lambda: self.cancel_process())
        cancel_button.grid(row=3, column=0, sticky="nsew")

        self.hide_progress_window()

    def show_progress_window(self):
        self.progress_window.deiconify()

    def hide_progress_window(self):
        self.progress_window.withdraw()

    def begin_progress(self):
        threading.Thread(target=self.show_progress).start()
        self.logger.info("Starting Cut")

    def end_progress(self, title, message):
        messagebox.showinfo(title, message)   

    def show_progress(self):
        title = ""
        message = ""
        for i in range(50):
            if self.cancel_flag:
                break
            else:
                self.progress_bar.step(2)
            time.sleep(0.1)
        if self.cancel_flag:
            title = "Cut Canceled"
            message = "The cut has been canceled manually."
            self.logger.info(f"{title} - {message}")
        else:
            title = "Cut Completed"
            message = "The cut has been completed successfully."
            self.logger.info(f"{title} - {message}")
        self.end_progress(title, message)


    def cancel_process(self):
        self.cancel_flag = True
  
