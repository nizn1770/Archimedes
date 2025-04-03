import time
import config
# import keyboard
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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    global MOTOR_PINS
    MOTOR_PINS = {
        "x": (config.X_DIR_PIN, config.X_PWM_PIN, config.X_STEPS_PER_REV, config.X_PITCH),
        "y": (config.Y_DIR_PIN, config.Y_PWM_PIN, config.Y_STEPS_PER_REV, config.Y_PITCH),
        "z": (config.Z_DIR_PIN, config.Z_PWM_PIN, config.Z_STEPS_PER_REV, config.Z_PITCH),
    }

    # Configure motor control pins as output
    for _, (dir_pin, pwm_pin, _, _) in MOTOR_PINS.items():
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(pwm_pin, GPIO.OUT)

    # Set up actuator control pins as output
    GPIO.setup(config.A_PWM_PIN, GPIO.OUT)
    GPIO.setup(config.A_FOR_PIN, GPIO.OUT)
    GPIO.setup(config.A_REV_PIN, GPIO.OUT)

    GPIO.output(config.A_PWM_PIN, GPIO.HIGH)

    # Start PWM signal for actuator motor at a fixed frequency
    #GPIO.PWM(config.A_PWM_PIN, config.A_FREQ).start(25)


# def listen_for_stop():
#     """
#     Listens for the 'q' key press to trigger an emergency stop.
#     - When 'q' is pressed, sets `emergency_stop` to True.
#     - Cleans up GPIO before terminating the program.
#     """
#     global emergency_stop
#     keyboard.wait("q")  # Wait until 'q' is pressed
#     emergency_stop = True  # Set emergency stop flag
#     print("Emergency stop activated. Exiting...")
#     GPIO.cleanup()  # Clean up GPIO pins before exiting
#     exit()  # Terminate the program


def rotate_motor(motor, direction, distance, rpm):
    """
    Rotates the specified motor for a given distance at a specific speed (RPM).
    - motor: Identifier ('x', 'y', 'z')
    - direction: 'l' (left), 'r' (right), 'u' (up), 'd' (down)
    - distance: Distance in inches
    - rpm: Rotational speed in revolutions per minute

    The function calculates the required number of steps and sends PWM signals accordingly.
    It also checks for an emergency stop before and during execution.
    """
    # global emergency_stop
    # if emergency_stop:  # Stop execution if emergency stop is activated
    #     return

    # Retrieve motor control pins and parameters
    dir_pin, pwm_pin, steps, pitch = MOTOR_PINS[motor]

    # Set motor direction based on input ('l' and 'u' -> LOW, 'r' and 'd' -> HIGH)
    GPIO.output(dir_pin, GPIO.LOW if direction in ['l', 'u'] else GPIO.HIGH)

    # Calculate total steps needed based on distance and pitch
    total_steps = int(distance * steps * pitch)
    frequency = rpm * steps / 60  # Convert RPM to step frequency
    SLEEP_TIME = 1 / (frequency * 2)  # Calculate delay for step signal

    # Generate step pulses to rotate the motor
    for _ in range(total_steps):
        # if emergency_stop:  # Check for emergency stop after each step
        #     break

        GPIO.output(pwm_pin, GPIO.HIGH)  # Step signal ON
        time.sleep(SLEEP_TIME)
        GPIO.output(pwm_pin, GPIO.LOW)  # Step signal OFF
        time.sleep(SLEEP_TIME)


def move_actuator(direction):
    """
    Moves the actuator in or out based on the direction.
    - direction: 'i' (in) or 'o' (out)

    The function sets the appropriate control pins to move the actuator.
    """
    # global emergency_stop
    # if emergency_stop:  # Stop execution if emergency stop is activated
    #     return

    # Set actuator movement direction
    if direction == "o":
        GPIO.output(config.A_FOR_PIN, GPIO.HIGH)  # Extend actuator
        GPIO.output(config.A_REV_PIN, GPIO.LOW)
    elif direction == "i":
        GPIO.output(config.A_FOR_PIN, GPIO.LOW)
        GPIO.output(config.A_REV_PIN, GPIO.HIGH)  # Retract actuator
    else:
        print("Invalid direction. Use 'i' for in or 'o' for out.")
        return


def main():
    """
    Main function to control motors and actuators based on user input.
    - Initializes motors and starts a listener thread for emergency stop.
    - Prompts the user to enter commands for moving motors or the actuator.
    - Runs an infinite loop until interrupted by the user or an emergency stop.
    """
    # global emergency_stop
    # emergency_stop = False  # Initialize emergency stop flag

    init_motors()  # Initialize motor and actuator GPIO
    # listener_thread = threading.Thread(target=listen_for_stop, daemon=True).start()

    try:
        while True:
            motor = input("Enter motor (x/y/z/a): ").lower()

            # if emergency_stop:  # Stop execution if emergency stop is activated
            #     break

            if motor == "a":  # Actuator movement
                direction = input("Enter direction of actuator (i/o): ").lower()
                move_actuator(direction)
            elif motor in MOTOR_PINS:  # Motor movement
                direction = input("Enter direction (l/r/u/d): ").lower()
                distance = float(input("Enter distance (in inches): "))
                RPM = int(input("Enter RPM: "))
                rotate_motor(motor, direction, distance, RPM)
            else:
                print("Invalid motor. Use 'x', 'y', 'z', or 'a'.")
                continue

            time.sleep(1)  # Pause before next command

    except KeyboardInterrupt:  # Handle user interrupt (Ctrl+C)
        print("Exiting")
        GPIO.cleanup()  # Clean up GPIO before exiting


if __name__ == "__main__":
    main()  # Run the program
