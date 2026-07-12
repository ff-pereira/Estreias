import logging

# General logger for info/debug
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/opt/estreias/backend/logs/estreias.log", encoding="utf-8")
    ]
)

# Error logger
error_logger = logging.getLogger("errors")
error_handler = logging.FileHandler("/opt/estreias/backend/logs/error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
