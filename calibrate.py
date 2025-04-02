import RPi.GPIO as GPIO
import time
import config
import keyboard
import threading


def init_motors():

    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    global MOTOR_PINS
    MOTOR_PINS = {
        "x": (config.X_DIR_PIN, config.X_PWM_PIN, config.X_STEPS_PER_REV, config.X_PITCH),
        "y": (config.Y_DIR_PIN, config.Y_PWM_PIN, config.Y_STEPS_PER_REV, config.Y_PITCH),
        "z": (config.Z_DIR_PIN, config.Z_PWM_PIN, config.Z_STEPS_PER_REV, config.Z_PITCH),
    }

    for _, (dir_pin, pwm_pin, _, _) in MOTOR_PINS.items():
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(pwm_pin, GPIO.OUT)

    GPIO.setup(config.A_PWM_PIN, GPIO.OUT)
    GPIO.setup(config.A_FOR_PIN, GPIO.OUT)
    GPIO.setup(config.A_REV_PIN, GPIO.OUT)

    GPIO.PWM(config.A_PWM_PIN, config.A_FREQ).start(25)



def listen_for_stop():
    global emergency_stop
    keyboard.wait("q")
    emergency_stop = True
    print("Emergency stop activated. Exiting...")
    GPIO.cleanup()
    exit()

def rotate_motor(motor, direction, distance, rpm):
    global emergency_stop
    if emergency_stop:
        return
    
    dir_pin, pwm_pin, steps, pitch = MOTOR_PINS[motor]

    GPIO.output(dir_pin, GPIO.LOW if direction in ['l', 'u'] else GPIO.HIGH)

    total_steps = int(distance * steps * pitch)
    frequency = rpm * steps / 60
    SLEEP_TIME = 1 / (frequency*2)

    for _ in range(total_steps):
        if emergency_stop:
            break

        GPIO.output(pwm_pin, GPIO.HIGH)
        time.sleep(SLEEP_TIME) 
        GPIO.output(pwm_pin, GPIO.LOW)
        time.sleep(SLEEP_TIME)

def move_actuator(direction):
    global emergency_stop
    if emergency_stop:
        return
    
    if direction == "o":
        GPIO.output(config.A_FOR_PIN, GPIO.HIGH)
        GPIO.output(config.A_REV_PIN, GPIO.LOW)
    elif direction == "i":
        GPIO.output(config.A_FOR_PIN, GPIO.LOW)
        GPIO.output(config.A_REV_PIN, GPIO.HIGH)
    else:
        print("Invalid direction. Use 'i' for in or 'o' for out.")
        return

def main():
    global emergency_stop
    emergency_stop = False

    init_motors()
    listener_thread = threading.Thread(target=listen_for_stop, daemon=True).start()



    try:
        while True:
            motor = input("Enter motor (x/y/z/a): ").lower()

            if emergency_stop:
                break

            if motor == "a":
                direction = input("Enter direction of actuator (i/o): ").lower()
                move_actuator(direction)
            elif motor in MOTOR_PINS:
                direction = input("Enter direction (l/r/u/d): ").lower()
                distance = float(input("Enter distance (in inches): "))
                RPM = int(input("Enter RPM: "))
                rotate_motor(motor, direction, distance, RPM)
            else:
                print("Invalid motor. Use 'x', 'y', 'z', or 'a'.")
                continue

            time.sleep(1)


    except KeyboardInterrupt:
        print("Exiting")
        GPIO.cleanup()

if __name__ == "__main__":
    main()