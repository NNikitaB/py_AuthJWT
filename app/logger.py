import logging

# setting logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Лог в файл
        logging.StreamHandler()          # Лог в консоль
    ]
)

logger = logging.getLogger(__name__)
