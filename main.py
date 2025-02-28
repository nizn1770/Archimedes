import touchscreen
import utils.logging_config 
from utils.logging_config import logger


def main():

    utils.logging_config.init_logging()
    logger.info("Archimedes started.")
    app = touchscreen.Application(logger)
    app.mainloop()




if __name__ == "__main__":
    main()