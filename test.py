import RPi.GPIO as GPIO
import time

# Define GPIO pins
##ground to pin 34, 4 up on the right side 
DIR_PIN = 36  # Use another available GPIO, 3 up on right side
PWM_PIN = 22  # PWM pin, 10 up on right side
PWM_FREQUENCY = 1000  # Frequency in Hz
STEPS_PER_REV = 1000  
SLEEP_TIME = 0.00025 

# GPIO setup
GPIO.setmode(GPIO.BOARD)  # Use BOARD numbering
GPIO.setwarnings(False)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.output(DIR_PIN, GPIO.HIGH)

# Setup PWM with 50% duty cycle
pwm = GPIO.PWM(PWM_PIN, PWM_FREQUENCY)


def rotate_motor(rotations, direction):

    if not direction:
        GPIO.output(DIR_PIN, GPIO.LOW)
        print("Direction: LEFT")
    else:
        GPIO.output(DIR_PIN, GPIO.HIGH)
        print("Direction: RIGHT")

    total_steps = int(rotations * STEPS_PER_REV)
    print(f"Rotating motor {rotations} rotations ({total_steps} steps)")

    for _ in range(total_steps):
        GPIO.output(PWM_PIN, GPIO.HIGH)
        time.sleep(SLEEP_TIME) 
        GPIO.output(PWM_PIN, GPIO.LOW)
        time.sleep(SLEEP_TIME)

    # pwm.start(50)  # Start PWM with 50% duty cycle
    # time.sleep(total_steps / PWM_FREQUENCY)
    # pwm.stop()


def test_motor():
    try:
        while True:
            rotations = float(input("Enter the number of rotations:"))
            dir = input("Enter 0 for left and 1 for right:")
            if dir == "0":
                rotate_motor(rotations, False)
            else:
                rotate_motor(rotations, True)

            
        
            

    except KeyboardInterrupt:
        print("\nExiting program.")
        pwm.stop()
        GPIO.cleanup()  # Cleanup GPIO on exit
