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

# Global PWM object for actuator
ACTUATOR_LOC = 0

def init_motors():
    """
    Initializes the motor GPIO pins and sets up the actuator control.
    - Configures GPIO mode and suppresses warnings.
    - Stores motor parameters (direction pin, PWM pin, steps per revolution, pitch) in a dictionary.
    - Sets the motor and actuator pins as output.
    - Starts the actuator's PWM signal at 25% duty cycle and leaves it running.
    """
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    global MOTOR_PINS, ACTUATOR_PWM
    MOTOR_PINS = {
        "x": (config.X_DIR_PIN, config.X_PWM_PIN, config.X_STEPS_PER_REV, config.X_PITCH),
        "y": (config.Y_DIR_PIN, config.Y_PWM_PIN, config.Y_STEPS_PER_REV, config.Y_PITCH),
        "z": (config.Z_DIR_PIN, config.Z_PWM_PIN, config.Z_STEPS_PER_REV, config.Z_PITCH),
    }

    # Configure motor control pins as output
    for _, (dir_pin, pwm_pin, _, _) in MOTOR_PINS.items():
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(pwm_pin, GPIO.OUT)

    GPIO.setup(config.A_VAL_PIN, GPIO.OUT)  # Actuator value pin setup
    GPIO.setup(config.A_PWM_PIN, GPIO.OUT)  # Actuator PWM pin setup
    GPIO.setup(config.A_FOR_PIN, GPIO.OUT)  # Actuator forward pin setup
    GPIO.setup(config.A_REV_PIN, GPIO.OUT)  # Actuator reverse pin setup

    GPIO.output(config.A_VAL_PIN, GPIO.HIGH)


def rotate_motor(motor, direction, distance, rpm):
    """
    Rotates the specified motor for a given distance at a specific speed (RPM) with ramp-up only.
    - motor: Identifier ('x', 'y', 'z')
    - direction: 'l' (left), 'r' (right), 'u' (up), 'd' (down)
    - distance: Distance in inches
    - rpm: Rotational speed in revolutions per minute

    The function calculates the required number of steps, applies a ramp-up phase followed by
    constant speed, and sends PWM signals accordingly. No ramp-down is performed.
    """
    # Retrieve motor control pins and parameters
    dir_pin, pwm_pin, steps, pitch = MOTOR_PINS[motor]

    # Set motor direction based on input ('l' and 'u' -> LOW, 'r' and 'd' -> HIGH)
    GPIO.output(dir_pin, GPIO.LOW if direction in ['l', 'u', 'o'] else GPIO.HIGH)

    # Calculate total steps needed based on distance and pitch
    total_steps = int(distance * steps * pitch)
    target_frequency = rpm * steps / 60  # Convert RPM to step frequency (steps per second)

    # Define ramp parameters (fixed ramp time in seconds for ramp-up)
    if motor in ["x", "y"]:
        RAMP_TIME = 3.0
    else:
        RAMP_TIME = 0.5  # Time for ramp-up (adjust as needed)
    ramp_steps = int(target_frequency * RAMP_TIME)  # Steps for ramp-up
    ramp_steps = max(1, min(ramp_steps, 200))  # Cap between 1 and 200 steps

    # Calculate frequency increment for ramp-up
    frequency_increment = target_frequency / ramp_steps if ramp_steps > 0 else target_frequency

    # Ramp-up phase
    for step in range(ramp_steps):
        current_frequency = frequency_increment * (step + 1)
        sleep_time = 1 / (current_frequency * 2)  # Calculate delay for step signal
        GPIO.output(pwm_pin, GPIO.HIGH)  # Step signal ON
        time.sleep(sleep_time)
        GPIO.output(pwm_pin, GPIO.LOW)  # Step signal OFF
        time.sleep(sleep_time)

    # Constant speed phase
    constant_steps = total_steps - ramp_steps  # Steps at full speed
    if constant_steps > 0:
        sleep_time = 1 / (target_frequency * 2)  # Sleep time for target frequency
        for _ in range(constant_steps):
            GPIO.output(pwm_pin, GPIO.HIGH)  # Step signal ON
            time.sleep(sleep_time)
            GPIO.output(pwm_pin, GPIO.LOW)  # Step signal OFF
            time.sleep(sleep_time)

def move_actuator(direction):
    """
    Moves the actuator in or out based on the direction with continuous PWM.
    - direction: 'i' (in) or 'o' (out)
    - duration: Time to run the actuator (seconds, default 1.0)

    The function sets the direction pins for the specified duration while the PWM signal
    remains running continuously.
    """
    global ACTUATOR_LOC

    if direction not in ["i", "o"]:
        print("Invalid direction. Use 'i' for in or 'o' for out.")
        return

    else:

        try:
            GPIO.output(config.A_PWM_PIN, GPIO.HIGH)  # Start PWM signal
            for _ in range(13):
                time.sleep(1)
                print("Actuator moving...")
                # Set actuator movement direction
                if direction == "i":
                    GPIO.output(config.A_FOR_PIN, GPIO.HIGH)  # Extend actuator
                    GPIO.output(config.A_REV_PIN, GPIO.LOW)
                elif direction == "o":  # direction == "i"
                    GPIO.output(config.A_FOR_PIN, GPIO.LOW)
                    GPIO.output(config.A_REV_PIN, GPIO.HIGH)  # Retract actuator

            GPIO.output(config.A_FOR_PIN, GPIO.LOW)  # Stop actuator movement
            GPIO.output(config.A_REV_PIN, GPIO.LOW)  # Stop actuator movement
            GPIO.output(config.A_PWM_PIN, GPIO.LOW)  # Stop PWM signal
            

        except Exception as e:
            print(f"Error in move_actuator: {e}")


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
            invalid = False
            motor = input("Enter motor (x/y/z/a): ").lower()

            # if emergency_stop:  # Stop execution if emergency stop is activated
            #     break

            if motor == "a":  # Actuator movement
                direction = input("Enter direction of actuator (i/o): ").lower()
                move_actuator(direction)
            elif motor in MOTOR_PINS:  # Motor movement
                if motor == "x":
                    direction = input("Enter direction (l/r): ").lower()
                elif motor == "y":
                    direction = input("Enter direction (u/d): ").lower()
                elif motor == "z":
                    direction = input("Enter direction (u/d): ").lower()
                else:
                    print("Invalid motor. Use 'x', 'y', or 'z'.")
                    invalid = True
                    continue
                if not invalid:
                    if motor == "z":
                        distance = float(input("Enter distance (in inches): "))
                        distance = distance * (1/3)
                    else:
                        distance = float(input("Enter distance (in inches): "))
                    RPM = int(input("Enter RPM: "))
                    rotate_motor(motor, direction, distance, RPM)
            else:
                print("Invalid motor. Use 'x', 'y', 'z', or 'a'.")
                continue

            time.sleep(1)  # Pause before next command

    except KeyboardInterrupt:  # Handle user interrupt (Ctrl+C)
        GPIO.output(config.A_PWM_PIN, GPIO.LOW)  # Stop PWM signal
        print("Exiting")
        GPIO.cleanup()  # Clean up GPIO before exiting


if __name__ == "__main__":
    main()  # Run the program
