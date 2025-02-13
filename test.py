# import RPi.GPIO as GPIO
# import time
# import keyboard  # Using keyboard module to detect key presses

# # Define GPIO pins
# ENABLE_PIN = 36  # Enable pin for motor driver
# DIR_PIN = 27  # Direction pin
# PUL_PIN = 22  # Pulse pin for step signal
# PWM_FREQUENCY = 5000  # Frequency set to 5kHz

# # GPIO setup
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(ENABLE_PIN, GPIO.OUT)
# GPIO.setup(DIR_PIN, GPIO.OUT)
# GPIO.setup(PUL_PIN, GPIO.OUT)
# GPIO.output(DIR_PIN, GPIO.HIGH)  # Set direction pin to default HIGH
# GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Enable starts HIGH

# # Setup PWM with 50% duty cycle
# pwm = GPIO.PWM(PUL_PIN, PWM_FREQUENCY)
# pwm.start(50)  # Start PWM with 50% duty cycle (runs continuously)

# enable_state = True  # Enable starts high
# direction_state = True  # Direction starts high

# try:
#     while True:
#         key = keyboard.read_event()
        
#         if key.event_type == keyboard.KEY_DOWN:
#             if key.name == "enter":  # Toggle enable
#                 enable_state = not enable_state
#                 GPIO.output(ENABLE_PIN, GPIO.LOW if enable_state else GPIO.HIGH)
#                 print("Enable toggled", "ON" if enable_state else "OFF")
#             elif key.name == "up" and enable_state:  # Toggle direction only if enabled
#                 direction_state = not direction_state
#                 GPIO.output(DIR_PIN, GPIO.HIGH if direction_state else GPIO.LOW)
#                 print("Direction toggled", "HIGH" if direction_state else "LOW")

# except KeyboardInterrupt:
#     print("\nExiting program.")
#     pwm.stop()
#     GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Ensure motor is disabled on exit
#     GPIO.cleanup()  # Cleanup GPIO on exit


import RPi.GPIO as GPIO
import time
import keyboard  # Using keyboard module to detect key presses

# Define GPIO pins
ENABLE_PIN = 36  # Enable pin for motor driver
DIR_PIN = 27  # Direction pin
PUL_PIN = 22  # Pulse pin for step signal

# Step settings
STEP_DELAY = 0.001  # Delay between step pulses (affects speed)
STEPS_PER_MOVE = 200  # Number of steps per movement command

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PUL_PIN, GPIO.OUT)

# Default states
GPIO.output(DIR_PIN, GPIO.HIGH)  # Set default direction
GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Enable starts HIGH (disabled)

enable_state = False  # Motor starts disabled
direction_state = True  # Default direction HIGH

def move_motor(steps):
    """Moves the stepper motor a set number of steps."""
    if not enable_state:  # Only move if enabled
        for _ in range(steps):
            GPIO.output(PUL_PIN, GPIO.HIGH)
            time.sleep(STEP_DELAY)
            GPIO.output(PUL_PIN, GPIO.LOW)
            time.sleep(STEP_DELAY)

try:
    print("Controls: ENTER = Toggle Enable, UP = Toggle Direction")
    
    while True:
        key = keyboard.read_event()

        if key.event_type == keyboard.KEY_DOWN:
            if key.name == "enter":  # Toggle enable
                enable_state = not enable_state
                GPIO.output(ENABLE_PIN, GPIO.LOW if enable_state else GPIO.HIGH)
                move_motor(STEPS_PER_MOVE)

                print("Enable toggled:", "OFF" if enable_state else "ON")

            elif key.name == "up" and enable_state:  # Toggle direction
                direction_state = not direction_state
                GPIO.output(DIR_PIN, GPIO.HIGH if direction_state else GPIO.LOW)
                print("Direction toggled:", "HIGH" if direction_state else "LOW")

            

except KeyboardInterrupt:
    print("\nExiting program.")
    GPIO.output(ENABLE_PIN, GPIO.HIGH)  # Ensure motor is disabled on exit
    GPIO.cleanup()  # Cleanup GPIO on exit
