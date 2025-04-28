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
    print(f"Total steps for {motor} motor: {total_steps}")
    target_frequency = rpm * steps / 60  # Convert RPM to step frequency (steps per second)

    # Define ramp parameters (fixed ramp time in seconds for ramp-up)
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
    
    rotate_motor("y", "u", config.MAX_VERTICAL, config.Y_RPM)  # Move Y-axis back to home
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

            print(f"Cutting {x_len} inches in X and {y_len} inches in Y")
            print(f"Moving down to height of cut...")
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
