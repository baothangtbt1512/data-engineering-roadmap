from src.config import logger
from src.extractor import ApiExtractor
from src.transformer import DataTransformer
from src.loader import PostgresLoader

def run_pipeline():
    logger.info("=== STARTING API TO POSTGRESQL ETL PIPELINE ===")
    
    extractor = ApiExtractor()
    transformer = DataTransformer()
    loader = PostgresLoader()

    try:
        # 1. Pipeline cho Users
        raw_users = extractor.fetch_data("users", limit=100)
        clean_users = transformer.transform_users(raw_users)
        loader.load_users(clean_users)

        # 2. Pipeline cho Products
        raw_products = extractor.fetch_data("products", limit=100)
        clean_products = transformer.transform_products(raw_products)
        loader.load_products(clean_products)

        # 3. Pipeline cho Orders (Carts)
        raw_orders = extractor.fetch_data("carts", limit=50)
        clean_orders = transformer.transform_orders(raw_orders)
        loader.load_orders(clean_orders)

        logger.info("=== ETL PIPELINE COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        logger.critical(f"ETL Pipeline failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    run_pipeline()