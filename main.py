import touchscreen
import cnc_control
from utils.logging_config import logger

def main():

    logger.info("Archimedes started.")
    touchscreen.init_touchscreen(logger)




if __name__ == "__main__":
    main()