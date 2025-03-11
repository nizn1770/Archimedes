import touchscreen
#import motor
import utils.logging_config 
from utils.logging_config import logger


def main():

    #initialize logging
    utils.logging_config.init_logging()
    logger.info("Archimedes started.")

    app = touchscreen.Application(logger)
    
    try:
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    finally:
        #motor.cleanup_motors()
        logger.info("Motors cleaned up.")
        logger.info("Archimedes stopped.")
        app.destroy()




if __name__ == "__main__":
    main()