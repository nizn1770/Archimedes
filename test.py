import RPi.GPIO as GPIO
import time

# Define GPIO pins
ENA_PIN = 37  # Physical pin 11
DIR_PIN = 36  # Use another available GPIO
PWM_PIN = 22  # PWM pin
PWM_FREQUENCY = 1000  # Frequency in Hz

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering
GPIO.setwarnings(False)
GPIO.setup(ENA_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.output(ENA_PIN, GPIO.HIGH)
GPIO.output(DIR_PIN, GPIO.HIGH)  # Set this pin to always HIGH

# Setup PWM with 50% duty cycle
pwm = GPIO.PWM(PWM_PIN, PWM_FREQUENCY)
pwm.start(50)

# Motor state variable
motor_on = False
direction_state = True 

try:
    while True:
        input("Press Enter to toggle direction...")  # Wait for Enter key press
        
        # Turn off PWM before changing direction
        GPIO.output(PWM_PIN, GPIO.LOW)  # Stop PWM
        time.sleep(0.1)  
        
        # Change direction
        direction_state = not direction_state  # Toggle direction
        GPIO.output(DIR_PIN, GPIO.HIGH if direction_state else GPIO.LOW)
        print(f"Direction: {'RIGHT' if direction_state else 'LEFT'}")
        
        # Turn PWM back on
        GPIO.output(PWM_PIN, GPIO.HIGH)  # Restart PWM

        
        # Short delay before next cycle
        time.sleep(0.1)
            

except KeyboardInterrupt:
    print("\nExiting program.")
    pwm.stop()
    GPIO.cleanup()  # Cleanup GPIO on exit
