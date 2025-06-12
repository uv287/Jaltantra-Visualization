# logger_config.py
import logging

logging.basicConfig(
    filename='dash_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s-%(funcName)s-%(lineno)d] - %(message)s',
    filemode='a'
)

logger = logging.getLogger(__name__)