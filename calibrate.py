import RPi.GPIO as GPIO
import time
import config

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(config.X_DIR_PIN, GPIO.OUT)
GPIO.setup(config.X_PWM_PIN, GPIO.OUT)
GPIO.setup(config.Y_DIR_PIN, GPIO.OUT)
GPIO.setup(config.Y_PWM_PIN, GPIO.OUT)
GPIO.setup(config.Z_DIR_PIN, GPIO.OUT)
GPIO.setup(config.Z_PWM_PIN, GPIO.OUT)

frequency = 2000

def rotate_motor(pin, distance, steps, frequency):

    total_steps = int(distance * steps)
    SLEEP_TIME = 1 / (frequency*2)

    for _ in range(total_steps):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(SLEEP_TIME) 
        GPIO.output(pin, GPIO.LOW)
        time.sleep(SLEEP_TIME)

try:
    while True:
        RPM = int(input("Enter RPM: "))
        motor = input("Enter motor (x/y/z): ")
        distance = float(input("Enter distance (in inches): "))
        
        if motor == "x":
            direction = input("Enter direction (l/r): ")
            if direction == "l":
                GPIO.output(config.X_DIR_PIN, GPIO.LOW)
            else:
                GPIO.output(config.X_DIR_PIN, GPIO.HIGH)

            frequency = RPM * config.X_STEPS_PER_REV / 60
            distance = distance * config.X_PITCH

            rotate_motor(config.X_PWM_PIN, distance, config.X_STEPS_PER_REV, frequency)

            
        if motor == "y":
            direction = input("Enter direction (u/d): ")
            if direction == "u":
                GPIO.output(config.Y_DIR_PIN, GPIO.LOW)
            else:
                GPIO.output(config.Y_DIR_PIN, GPIO.HIGH)

            frequency = RPM * config.Y_STEPS_PER_REV / 60
            distance = distance * config.Y_PITCH

            rotate_motor(config.Y_PWM_PIN, distance, config.Y_STEPS_PER_REV, frequency)

        if motor == "z":
            direction = input("Enter direction (u/d): ")
            if direction == "u":
                GPIO.output(config.Z_DIR_PIN, GPIO.LOW)
            else:
                GPIO.output(config.Z_DIR_PIN, GPIO.HIGH)

            frequency = RPM * config.X_STEPS_PER_REV / 60

            rotate_motor(config.Z_PWM_PIN, distance, config.Z_STEPS_PER_REV, frequency)
            
        time.sleep(1)



except KeyboardInterrupt:
    print("Exiting")
    GPIO.cleanup()

