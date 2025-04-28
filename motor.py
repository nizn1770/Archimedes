import time
import config
#import keyboard
import threading

# Set this to True when running on Raspberry Pi
RUN_ON_PI = True

# Conditionally import RPi.GPIO
if RUN_ON_PI:
    import RPi.GPIO as GPIO
else:
    class GPIO_Mock:
        BOARD = "BOARD"
        OUT = "OUT"
        LOW = "LOW"
        HIGH = "HIGH"

        def setmode(self, mode):
            print(f"Mock GPIO: Set mode {mode}")
            

        def setwarnings(self, flag):
            print(f"Mock GPIO: Set warnings {flag}")

        def setup(self, pin, mode):
            print(f"Mock GPIO: Setup pin {pin} as {mode}")

        def output(self, pin, state):
            #print(f"Mock GPIO: Set pin {pin} to {state}")
            return 1

        def PWM(self, pin, freq):
            print(f"Mock GPIO: Start PWM on pin {pin} with frequency {freq}")
            return self.MockPWM()

        def cleanup(self):
            print("Mock GPIO: Cleanup")

        class MockPWM:
            def start(self, duty_cycle):
                print(f"Mock PWM: Started with duty cycle {duty_cycle}")

    GPIO = GPIO_Mock()  # Use mock GPIO when not on Pi

def init_motors():
    """
    Initializes the motor GPIO pins and sets up the actuator control.
    - Configures GPIO mode and suppresses warnings.
    - Stores motor parameters (direction pin, PWM pin, steps per revolution, pitch) in a dictionary.
    - Sets the motor and actuator pins as output.
    - Starts the actuator's PWM signal at 25% duty cycle.
    """
    GPIO.setmode(GPIO.BOARD)  # Set GPIO mode to BOARD numbering
    GPIO.setwarnings(False)  # Suppress GPIO warnings

    global MOTOR_PINS
    MOTOR_PINS = {
        "x": (config.X_DIR_PIN, config.X_PWM_PIN, config.X_STEPS_PER_REV, config.X_PITCH),
        "y": (config.Y_DIR_PIN, config.Y_PWM_PIN, config.Y_STEPS_PER_REV, config.Y_PITCH),
        "z": (config.Z_DIR_PIN, config.Z_PWM_PIN, config.Z_STEPS_PER_REV, config.Z_PITCH),
    }

    for _, (dir_pin, pwm_pin, _, _) in MOTOR_PINS.items():
        GPIO.setup(dir_pin, GPIO.OUT)  # Set direction pin as output
        GPIO.setup(pwm_pin, GPIO.OUT)  # Set PWM pin as output

    GPIO.setup(config.A_PWM_PIN, GPIO.OUT)  # Actuator PWM pin setup
    GPIO.setup(config.A_FOR_PIN, GPIO.OUT)  # Actuator forward pin setup
    GPIO.setup(config.A_REV_PIN, GPIO.OUT)  # Actuator reverse pin setup

    GPIO.PWM(config.A_PWM_PIN, config.A_FREQ).start(25)  # Start actuator PWM at 25% duty cycle

def cleanup_motors():
    """
    Cleans up the GPIO pins to reset them to their default state.
    """
    GPIO.cleanup()

# def listen_for_stop():
#     """
#     Listens for an emergency stop key ('q') and stops all motor operations when triggered.
#     """
#     global emergency_stop
#     keyboard.wait("q")  # Wait for 'q' key press to trigger emergency stop
#     emergency_stop = True
#     print("Emergency stop activated. Exiting...")
#     GPIO.cleanup()
#     exit()

def rotate_motor(motor, direction, distance, rpm):
    """
    Rotates the specified motor in the given direction for a set distance at a specified RPM.
    - Converts distance to step count based on motor parameters.
    - Sets direction based on user input.
    - Executes motor steps unless an emergency stop is triggered.
    """
    # global emergency_stop
    # if emergency_stop:
    #     return
    
    dir_pin, pwm_pin, steps, pitch = MOTOR_PINS[motor]
    GPIO.output(dir_pin, GPIO.LOW if direction in ['l', 'u', 'i'] else GPIO.HIGH)  # Set motor direction

    total_steps = int(distance * steps * pitch)  # Calculate total steps needed
    frequency = rpm * steps / 60  # Convert RPM to step frequency
    SLEEP_TIME = 1 / (frequency * 2)  # Calculate delay between steps

    print(f"frequency: {frequency} steps/s Sleep time: {SLEEP_TIME} seconds total_steps: {total_steps}")

    for step in range(total_steps):
        # if emergency_stop:
        #     break
        if step % (steps*pitch) == 0:
            print(f"Motor {motor} traveled {step / (steps * pitch)} inches in direction {direction}")

        GPIO.output(pwm_pin, GPIO.HIGH)  # Activate PWM pin
        time.sleep(SLEEP_TIME) 
        GPIO.output(pwm_pin, GPIO.LOW)  # Deactivate PWM pin
        time.sleep(SLEEP_TIME)
    print(f"Motor {motor} traveled {total_steps / (steps * pitch)} inches in direction {direction}")

def move_actuator(direction):
    """
    Moves the actuator in the specified direction ('o' for out, 'i' for in).
    """
    # global emergency_stop
    # if emergency_stop:
    #     return
    
    if direction == "o":
        print("Moving actuator out")
        GPIO.output(config.A_FOR_PIN, GPIO.HIGH)
        GPIO.output(config.A_REV_PIN, GPIO.LOW)
    elif direction == "i":
        print("Moving actuator in")
        GPIO.output(config.A_FOR_PIN, GPIO.LOW)
        GPIO.output(config.A_REV_PIN, GPIO.HIGH)
    else:
        print("Invalid direction. Use 'i' for in or 'o' for out.")
        return
    
    for _ in range(5):
        time.sleep(1)
        print("Actuator moving...")

def move_head(direction):
    """
    Moves the cutting head along the Z-axis in the specified direction.
    """
    # global emergency_stop
    # if emergency_stop:
    #     return
    print(f"Moving head {direction}")
    rotate_motor("z", direction, config.Z_JOG, config.Z_RPM)  

def return_to_home(x_len, y_len):
    """
    Returns the machine to its home position after a cutting operation.
    - Moves head up, retracts actuator, and repositions X and Y axes.
    """
    # global emergency_stop
    # if emergency_stop:
    #     return
    print("Returning to home position...")
    move_head("o")  # Raise the cutting head
    move_actuator("i")  # Retract actuator
    
    rotate_motor("y", "u", y_len, config.Y_RPM)  # Move Y-axis back to home
    rotate_motor("x", "l", x_len, config.X_RPM)  # Move X-axis back to home
    

def main():
    """
    Main function to run the cutting sequence.
    - Initializes motors and starts emergency stop listener.
    - Accepts user input for cut dimensions and executes the cutting sequence.
    - Returns to home position after cutting and waits for user confirmation.
    """
    # global emergency_stop
    # emergency_stop = False

    init_motors()

    # Start the emergency stop listener in a separate thread
    # stop_thread = threading.Thread(target=listen_for_stop, daemon=True).start()

    print(f"{config.X_RPM} X {config.Y_RPM} Y")

    try:
        while True:
            x_len = int(input("Enter the length of the X cut in inches: "))  # Get X cut length from user
            y_len = int(input("Enter the length of the Y cut in inches: "))  # Get Y cut length from user


            rotate_motor("y", "d", config.MAX_VERTICAL - y_len, config.Y_RPM)
            move_actuator("o")  # Extend actuator
            move_head("i")  # Lower cutting head

            rotate_motor("x", "r", config.MAX_HORIZONTAL, config.X_RPM)

            move_head("o")  # Raise cutting head

            input("Remove scrap piece of panel and press Enter to continue...")

            rotate_motor("x", "l", config.MAX_HORIZONTAL - x_len, config.X_RPM)
            move_actuator("i")  # Retract actuator
            move_head("i")  # Lower cutting head

            rotate_motor("y", "d", y_len, config.Y_RPM)
            
            print("Cutting complete. Returning to home position...")
            return_to_home(x_len, y_len)

            input("Returned to home position. Remove panel and scrap piece and press Enter to continue...")    
    
    except KeyboardInterrupt:
        print("Exiting")
        GPIO.cleanup()

if __name__ == "__main__":
    main()
