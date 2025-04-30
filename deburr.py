import time
import config
# import keyboard
import threading

# Set this to True when running on Raspberry Pi
RUN_ON_PI = True

import RPi.GPIO as GPIO

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
    if motor == "x":
        RAMP_TIME = 1.5
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

def move_x():
    while True:
        rotate_motor("x", "r", 48, 5)
        rotate_motor("x", "l", 48, 5)

def move_y():
    while True:
        rotate_motor("y", "d", 48, 10)
        rotate_motor("y", "u", 48, 10)


def main():
    
    init_motors()  

    try:
        # # Start the motor movement in separate threads
        # x_thread = threading.Thread(target=move_x)
        # y_thread = threading.Thread(target=move_y)

        # x_thread.start()
        # y_thread.start()

        # # Wait for both threads to finish (they won't in this case)
        # x_thread.join()
        # y_thread.join()

        move_x()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Exiting program.")

if __name__ == "__main__":
    main()  # Run the program
