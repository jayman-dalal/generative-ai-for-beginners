import logging

import colorlog

INFO_HEADER_H1_LEVEL = 21
logging.addLevelName(INFO_HEADER_H1_LEVEL, "INFOH1")

def infoh1(self, message, *args, **kwargs):
    """Custom method for logging SPECIAL_INFO messages."""
    if self.isEnabledFor(INFO_HEADER_H1_LEVEL):
        self._log(INFO_HEADER_H1_LEVEL, message, args, **kwargs)

def setup_logger(logger: logging.Logger) -> logging.Logger:
    """Set up a logger with colored output."""
    logger.setLevel(logging.INFO)

    # Create a console handler
    console_handler = logging.StreamHandler()

    # Define the color format
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s.%(msecs)03d %(name)s:%(funcName)s:%(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "white",
            "INFOH1": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    # Set the formatter for the console handler
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger

# Add the custom method to the Logger class
logging.Logger.infoh1 = infoh1