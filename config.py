import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from io import BytesIO

#MAX CUTS IN INCHES
MAX_HORIZONTAL = 48
MAX_VERTICAL = 48

#MIN CUTS IN INCHES
MIN_HORIZONTAL = 1
MIN_VERTICAL = 1


STEPS_PER_INCH = 1000

SERIAL_PORT = ""
BAUD_RATE = 0

DELETE_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/delete.png"
NEXT_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/checkmark.png"