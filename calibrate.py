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
GPIO.setup(config.A_PWM_PIN, GPIO.OUT)
GPIO.setup(config.A_FOR_PIN, GPIO.OUT)
GPIO.setup(config.A_REV_PIN, GPIO.OUT)

GPIO.PWM(config.A_PWM_PIN).start(25)

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
        motor = input("Enter motor (x/y/z/a): ")

        if motor == "a":
            direction = input("Enter direction of actuator (i/o): ")
            if direction == "o":
                GPIO.output(config.A_FOR_PIN, GPIO.HIGH)
                GPIO.output(config.A_REV_PIN, GPIO.LOW)
            elif direction == "i":
                GPIO.output(config.A_FOR_PIN, GPIO.LOW)
                GPIO.output(config.A_REV_PIN, GPIO.HIGH)
            else:
                print("Invalid direction. Use 'i' for in or 'o' for out.")
                continue
            
        
        if motor == "x":
            direction = input("Enter direction (l/r): ")
            distance = float(input("Enter distance (in inches): "))
            RPM = int(input("Enter RPM: "))

            if direction == "l":
                GPIO.output(config.X_DIR_PIN, GPIO.LOW)
            elif direction == "r":
                GPIO.output(config.X_DIR_PIN, GPIO.HIGH)
            else:
                print("Invalid direction. Use 'l' for left or 'r' for right.")
                continue

            frequency = RPM * config.X_STEPS_PER_REV / 60
            distance = distance * config.X_PITCH

            rotate_motor(config.X_PWM_PIN, distance, config.X_STEPS_PER_REV, frequency)

            
        if motor == "y":
            direction = input("Enter direction (u/d): ")
            distance = float(input("Enter distance (in inches): "))
            RPM = int(input("Enter RPM: "))

            if direction == "u":
                GPIO.output(config.Y_DIR_PIN, GPIO.LOW)
            elif direction == "d":
                GPIO.output(config.Y_DIR_PIN, GPIO.HIGH)
            else:
                print("Invalid direction. Use 'u' for up or 'd' for down.")
                continue

            frequency = RPM * config.Y_STEPS_PER_REV / 60
            distance = distance * config.Y_PITCH

            rotate_motor(config.Y_PWM_PIN, distance, config.Y_STEPS_PER_REV, frequency)

        if motor == "z":
            direction = input("Enter direction (u/d): ")
            distance = float(input("Enter distance (in inches): "))
            RPM = int(input("Enter RPM: "))

            if direction == "u":
                GPIO.output(config.Z_DIR_PIN, GPIO.LOW)
            elif direction == "d":
                GPIO.output(config.Z_DIR_PIN, GPIO.HIGH)
            else:
                print("Invalid direction. Use 'u' for up or 'd' for down.")
                continue

            frequency = RPM * config.X_STEPS_PER_REV / 60

            rotate_motor(config.Z_PWM_PIN, distance, config.Z_STEPS_PER_REV, frequency)
            
        time.sleep(1)



except KeyboardInterrupt:
    print("Exiting")
    GPIO.cleanup()

