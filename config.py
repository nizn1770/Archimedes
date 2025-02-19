import requests
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
MIN_HORIZONTAL = 12
MIN_VERTICAL = 12


STEPS_PER_INCH = 200

SERIAL_PORT = ""
BAUD_RATE = 0

DELETE_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/delete.png"
NEXT_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/checkmark.png"