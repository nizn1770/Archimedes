import RPi.GPIO as GPIO
import time

# Define GPIO pins
ENA_PIN = 37  # Physical pin 11
DIR_PIN = 36  # Use another available GPIO
PWM_PIN = 22  # PWM pin
PWM_FREQUENCY = 1000  # Frequency in Hz
STEPS_PER_REV = 200  

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering
GPIO.setwarnings(False)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.output(DIR_PIN, GPIO.HIGH)

# Setup PWM with 50% duty cycle
pwm = GPIO.PWM(PWM_PIN, PWM_FREQUENCY)
pwm.start(50)
GPIO.output(PWM_PIN, GPIO.LOW)


def rotate_motor(rotations):
    GPIO.output(PWM_PIN, GPIO.LOW)

    total_steps = int(rotations * STEPS_PER_REV)
    print(f"Rotating motor {rotations} rotations ({total_steps} steps)")

    for _ in range(total_steps):

        GPIO.output(PWM_PIN, GPIO.HIGH)
        time.sleep(1 / (2 * PWM_FREQUENCY))
        GPIO.output(PWM_PIN, GPIO.LOW)
        time.sleep(1 / (2 * PWM_FREQUENCY))


try:
    while True:
        rotations = float(input("Enter the number of rotations:"))
        dir = input("Enter 0 for left and 1 for right:")
        if dir == "0":
            GPIO.output(DIR_PIN, GPIO.LOW)
            print("Direction: LEFT")
        else:
            GPIO.output(DIR_PIN, GPIO.HIGH)
            print("Direction: RIGHT")

        rotate_motor(rotations)
        
            

except KeyboardInterrupt:
    print("\nExiting program.")
    pwm.stop()
    GPIO.cleanup()  # Cleanup GPIO on exit
