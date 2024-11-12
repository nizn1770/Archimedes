import touchscreen
import cnc_control
import utils.logging_config 
from utils.logging_config import logger


def main():

    utils.logging_config.init_logging()
    logger.info("Archimedes started.")
    touchscreen.init_touchscreen(logger)




if __name__ == "__main__":
    main()