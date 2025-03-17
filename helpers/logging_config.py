import logging

# Configure logging with a custom format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(name)s:%(funcName)s:%(levelname)s - %(message)s',
    datefmt='%y-%m-%d %H:%M:%S'
)