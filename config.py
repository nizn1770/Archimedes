#import requests
#import RPi.GPIO as GPIO
import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import messagebox
from io import BytesIO


GEOMETRY = "800x480"

#MAX CUTS IN INCHES
MAX_HORIZONTAL = 48
MAX_VERTICAL = 48

#MIN CUTS IN INCHES
MIN_HORIZONTAL = 1
MIN_VERTICAL = 1

#Machine pin set ups
X_DIR_PIN = 11
X_PWM_PIN = 13
X_RPM = 100
X_STEPS_PER_REV = 1000
X_PITCH = 4

Y_DIR_PIN = 15
Y_PWM_PIN = 16
Y_RPM = 100
Y_STEPS_PER_REV = 1000
Y_PITCH = 5

Z_DIR_PIN = 18
Z_PWM_PIN = 22
Z_STEPS_PER_REV = 1000

# motor_configs = {
#         'x': {
#             'dir_pin': X_DIR_PIN,
#             'pwm_pin': X_PWM_PIN,
#             'rpm': X_RPM,
#             'steps_per_rev': X_STEPS_PER_REV,
#             'pitch': X_PITCH,
#             'direction': {'l': GPIO.LOW, 'r': GPIO.HIGH}},
#         'y': {
#             'dir_pin': Y_DIR_PIN,
#             'pwm_pin': Y_PWM_PIN,
#             'rpm': Y_RPM,
#             'steps_per_rev': Y_STEPS_PER_REV,
#             'pitch': Y_PITCH,
#             'direction': {'u': GPIO.LOW, 'd': GPIO.HIGH}}
#     }


DELETE_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/delete.png"
NEXT_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/checkmark.png"
LOGO_IMAGE = "https://raw.githubusercontent.com/nizn1770/Archimedes/main/images/logo.png"