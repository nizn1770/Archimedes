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

#Machine pin set ups
X_DIR_PIN = 11
X_PWM_PIN = 13

X_PWM_FREQUENCY = 2000
X_STEPS_PER_REV = 1000

Y_DIR_PIN = 15
Y_PWM_PIN = 16

Y_PWM_FREQUENCY = 2000
Y_STEPS_PER_REV = 1000

Z_DIR_PIN = 18
Z_PWM_PIN = 22

Z_PWM_FREQUENCY = 2000
Z_STEPS_PER_REV = 1000


DELETE_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/delete.png"
NEXT_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/checkmark.png"