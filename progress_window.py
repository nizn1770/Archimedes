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
    def __init__(self, parent, logger, message_var):
        self.logger = logger
        self.message_var = message_var
        
        self.cancel_flag = False

        self.progress_window = tk.Toplevel(parent)
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

        self.hide_progress_window()

    def show_progress_window(self):
        self.progress_window.deiconify()

    def hide_progress_window(self):
        self.progress_window.withdraw()

    def begin_progress(self):
        self.cancel_flag = False
        self.progress_bar["value"]=0
        threading.Thread(target=self.cut).start()
        self.logger.info("Starting Cut") 

    def cut(self):
        for i in range(50):
            if self.cancel_flag:
                self.cut_title = "Cut Canceled"
                self.cut_message = "The cut has been canceled without completing."
                break
            else:
                self.progress_bar.step(2)
            time.sleep(0.1)
        if not self.cancel_flag:
            self.cut_title = "Cut Completed"
            self.cut_message = "The cut has been completed successfully"
        self.logger.info(f"{self.cut_title} - {self.cut_message}")
        print("done")
        self.hide_progress_window()
        
    def get_cut_message(self):
        return self.cut_title, self.cut_message


    def cancel_process(self):
        self.cancel_flag = True
  