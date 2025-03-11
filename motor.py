#import RPi.GPIO as GPIO
import time
import config

def init_motors():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    for pin in [config.X_DIR_PIN, config.X_PWM_PIN, config.Y_DIR_PIN, config.Y_PWM_PIN]:
        GPIO.setup(pin, GPIO.OUT)
        
def cleanup_motors():
    GPIO.cleanup()

def move_motor(motor, distance, direction):
    if motor not in config.motor_configs:
        print("Invalid motor specified.")
        return


    config_data = config.motor_configs[motor]

    #configure direction
    GPIO.output(config_data['dir_pin'], config_data['direction'][direction])

    #calculate steps and time
    total_steps = int(distance * config_data['steps_per_rev'] * config_data['pitch'])
    sleep_time = frequency_sleep_time(RPM_to_frequency(config_data['rpm']))

    #move motor
    for _ in range(total_steps):

        GPIO.output(config_data['pwm_pin'], GPIO.HIGH)
        time.sleep(sleep_time)
        GPIO.output(config_data['pwm_pin'], GPIO.LOW)
        time.sleep(sleep_time)

    


def RPM_to_frequency(rpm):
    return rpm * 2000 / 60

def frequency_sleep_time(frequency):
    return 1 / (frequency*2)