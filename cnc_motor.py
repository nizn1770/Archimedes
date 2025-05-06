import time
import config
import RPi.GPIO as GPIO
import logging

# Configure logger for standalone use
logger = logging.getLogger(__name__)

def init_motors():
    """
    Initializes the motor GPIO pins and sets up the actuator control.
    - Configures GPIO mode and suppresses warnings.
    - Stores motor parameters (direction pin, PWM pin, steps per revolution, pitch) in a dictionary.
    - Sets the motor and actuator pins as output.
    - Starts the actuator's PWM signal at 25% duty cycle.
    """
    logger.info("Initializing motors")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    global MOTOR_PINS
    MOTOR_PINS = {
        "x": (config.X_DIR_PIN, config.X_PWM_PIN, config.X_STEPS_PER_REV, config.X_PITCH),
        "y": (config.Y_DIR_PIN, config.Y_PWM_PIN, config.Y_STEPS_PER_REV, config.Y_PITCH),
        "z": (config.Z_DIR_PIN, config.Z_PWM_PIN, config.Z_STEPS_PER_REV, config.Z_PITCH),
    }
    logger.debug(f"Motor pins configured: {MOTOR_PINS}")

    for motor, (dir_pin, pwm_pin, _, _) in MOTOR_PINS.items():
        GPIO.setup(dir_pin, GPIO.OUT)
        GPIO.setup(pwm_pin, GPIO.OUT)
        logger.debug(f"Set up {motor} motor: dir_pin={dir_pin}, pwm_pin={pwm_pin}")

    GPIO.setup(config.A_PWM_PIN, GPIO.OUT)
    GPIO.setup(config.A_FOR_PIN, GPIO.OUT)
    GPIO.setup(config.A_REV_PIN, GPIO.OUT)
    logger.debug(f"Actuator pins set up: A_PWM_PIN={config.A_PWM_PIN}, A_FOR_PIN={config.A_FOR_PIN}, A_REV_PIN={config.A_REV_PIN}")

    GPIO.output(config.A_PWM_PIN, GPIO.HIGH)
    logger.info("Actuator PWM signal set to HIGH")

def cleanup_motors():
    """
    Cleans up the GPIO pins to reset them to their default state.
    """
    logger.info("Cleaning up motor GPIO pins")
    GPIO.cleanup()

def rotate_motor(motor, direction, distance, rpm):
    """
    Rotates the specified motor for a given distance at a specific speed (RPM) with ramp-up only.
    - motor: Identifier ('x', 'y', 'z')
    - direction: 'l' (left), 'r' (right), 'u' (up), 'd' (down)
    - distance: Distance in inches
    - rpm: Rotational speed in revolutions per minute
    """
    logger.info(f"Rotating {motor} motor: direction={direction}, distance={distance} in, rpm={rpm}")
    dir_pin, pwm_pin, steps, pitch = MOTOR_PINS[motor]
    logger.debug(f"Using pins: dir_pin={dir_pin}, pwm_pin={pwm_pin}, steps={steps}, pitch={pitch}")

    GPIO.output(dir_pin, GPIO.LOW if direction in ['l', 'u', 'o'] else GPIO.HIGH)
    logger.debug(f"Set {motor} direction to {'LOW' if direction in ['l', 'u', 'o'] else 'HIGH'}")

    total_steps = int(distance * steps * pitch)
    logger.info(f"Calculated total steps for {motor}: {total_steps}")
    target_frequency = rpm * steps / 60
    logger.debug(f"Target frequency: {target_frequency} Hz")

    RAMP_TIME = 0.5
    ramp_steps = int(target_frequency * RAMP_TIME)
    ramp_steps = max(1, min(ramp_steps, 200))
    logger.debug(f"Ramp steps: {ramp_steps}, ramp time: {RAMP_TIME} s")

    frequency_increment = target_frequency / ramp_steps if ramp_steps > 0 else target_frequency
    logger.debug(f"Frequency increment: {frequency_increment}")

    for step in range(ramp_steps):
        current_frequency = frequency_increment * (step + 1)
        sleep_time = 1 / (current_frequency * 2)
        GPIO.output(pwm_pin, GPIO.HIGH)
        time.sleep(sleep_time)
        GPIO.output(pwm_pin, GPIO.LOW)
        time.sleep(sleep_time)
    logger.debug("Completed ramp-up phase")

    constant_steps = total_steps - ramp_steps
    if constant_steps > 0:
        sleep_time = 1 / (target_frequency * 2)
        for _ in range(constant_steps):
            GPIO.output(pwm_pin, GPIO.HIGH)
            time.sleep(sleep_time)
            GPIO.output(pwm_pin, GPIO.LOW)
            time.sleep(sleep_time)
        logger.debug(f"Completed {constant_steps} constant speed steps")

def move_actuator(direction):
    """
    Moves the actuator in the specified direction ('o' for out, 'i' for in).
    """
    logger.info(f"Moving actuator: direction={direction}")
    if direction == "o":
        logger.debug("Setting actuator to move out")
        GPIO.output(config.A_FOR_PIN, GPIO.HIGH)
        GPIO.output(config.A_REV_PIN, GPIO.LOW)
    elif direction == "i":
        logger.debug("Setting actuator to move in")
        GPIO.output(config.A_FOR_PIN, GPIO.LOW)
        GPIO.output(config.A_REV_PIN, GPIO.HIGH)
    else:
        logger.error(f"Invalid actuator direction: {direction}. Use 'i' for in or 'o' for out.")
        return
    
    for _ in range(13):
        time.sleep(1)
        logger.debug("Actuator moving...")

def move_head(direction):
    """
    Moves the cutting head along the Z-axis in the specified direction.
    """
    logger.info(f"Moving head: direction={direction}")
    rotate_motor("z", direction, config.Z_JOG, config.Z_RPM)

def return_to_home(x_len, y_len):
    """
    Returns the machine to its home position after a cutting operation.
    - Moves head up, retracts actuator, and repositions X and Y axes.
    """
    logger.info(f"Returning to home position: x_len={x_len}, y_len={y_len}")
    move_head("o")
    move_actuator("i")
    rotate_motor("y", "u", config.MAX_VERTICAL, config.Y_RPM)
    rotate_motor("x", "l", x_len, config.X_RPM)
    logger.info("Home position reached")

def return_to_home_from_hor_cut(y_len):
    """
    Returns the machine to its home position from the horizontal cut location.
    - Assumes head is lowered and actuator is extended.
    - Raises head, retracts actuator, moves Y-axis to home, and X-axis to home.
    """
    logger.info(f"Returning to home from horizontal cut: y_len={y_len}")
    move_actuator("i")
    rotate_motor("y", "u", config.MAX_VERTICAL - y_len, config.Y_RPM)
    rotate_motor("x", "l", config.MAX_HORIZONTAL, config.X_RPM)
    logger.info("Home position reached from horizontal cut")

def make_hor_cut(y_len):
    """
    Performs the horizontal cut by moving Y-axis, extending actuator, lowering head, and moving X-axis.
    """
    logger.info(f"Starting horizontal cut: y_len={y_len}")
    rotate_motor("y", "d", config.MAX_VERTICAL - y_len, config.Y_RPM)
    move_actuator("o")
    move_head("i")
    rotate_motor("x", "r", config.MAX_HORIZONTAL, config.X_RPM)
    move_head("o")
    logger.info("Horizontal cut completed")

def make_ver_cut(x_len, y_len):
    """
    Performs the vertical cut by moving X-axis, retracting actuator, lowering head, and moving Y-axis.
    """
    logger.info(f"Starting vertical cut: x_len={x_len}, y_len={y_len}")
    rotate_motor("x", "l", config.MAX_HORIZONTAL - x_len, config.X_RPM)
    move_actuator("i")
    move_head("i")
    rotate_motor("y", "d", y_len, config.Y_RPM)
    logger.info("Vertical cut completed")

def main():
    """
    Main function to run the cutting sequence for testing.
    """
    logger.info("Starting motor test sequence")
    init_motors()
    try:
        while True:
            x_len = int(input("Enter the length of the X cut in inches: "))
            y_len = int(input("Enter the length of the Y cut in inches: "))
            logger.info(f"Test cut initiated: x_len={x_len}, y_len={y_len}")
            make_hor_cut(y_len)
            input("Remove scrap piece of panel and press Enter to continue...")
            make_ver_cut(x_len, y_len)
            logger.info("Cutting complete. Returning to home position...")
            return_to_home(x_len, y_len)
            input("Returned to home position. Remove panel and scrap piece and press Enter to continue...")
    except KeyboardInterrupt:
        logger.info("Test sequence interrupted by user")
        cleanup_motors()

if __name__ == "__main__":
    main()