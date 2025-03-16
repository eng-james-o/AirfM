import logging.config
import yaml

def setup_logging(config_path="logging.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)

setup_logging()

logger = logging.getLogger("airfm")