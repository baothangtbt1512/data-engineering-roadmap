import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Database
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "ecommerce_analytics")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()

API_BASE_URL = os.getenv("API_BASE_URL", "https://dummyjson.com")

# Đảm bảo thư mục logs tồn tại
os.makedirs("logs", exist_ok=True)

# Thiết lập Logging
log_format = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("logs/etl_pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ETL_Pipeline")