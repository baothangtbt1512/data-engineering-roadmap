import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Tuple
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, logger

class PostgresLoader:
    def __init__(self):
        # Thiết lập thông tin kết nối
        self.conn_params = {
            "host": DB_HOST,
            "port": DB_PORT,
            "dbname": DB_NAME,
            "user": DB_USER
        }
        # Chỉ truyền password nếu có giá trị thực sự
        if DB_PASSWORD:
            self.conn_params["password"] = DB_PASSWORD

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def load_users(self, records: List[Tuple]):
        query = """
            INSERT INTO api_users (user_id, full_name, email, gender, city)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                full_name = EXCLUDED.full_name,
                email = EXCLUDED.email,
                gender = EXCLUDED.gender,
                city = EXCLUDED.city;
        """
        self._batch_insert(query, records, "api_users")

    def load_products(self, records: List[Tuple]):
        query = """
            INSERT INTO api_products (product_id, title, category, price, stock)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                title = EXCLUDED.title,
                category = EXCLUDED.category,
                price = EXCLUDED.price,
                stock = EXCLUDED.stock;
        """
        self._batch_insert(query, records, "api_products")

    def load_orders(self, records: List[Tuple]):
        query = """
            INSERT INTO api_orders (order_id, user_id, total_products, total_quantity, total_amount, discounted_total)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO UPDATE SET
                total_products = EXCLUDED.total_products,
                total_quantity = EXCLUDED.total_quantity,
                total_amount = EXCLUDED.total_amount,
                discounted_total = EXCLUDED.discounted_total;
        """
        self._batch_insert(query, records, "api_orders")

    def _batch_insert(self, query: str, records: List[Tuple], table_name: str):
        if not records:
            logger.warning(f"No records to insert into {table_name}")
            return
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    execute_batch(cur, query, records, page_size=100)
                conn.commit()
            logger.info(f"Successfully upserted {len(records)} records into {table_name}")
        except psycopg2.DatabaseError as e:
            logger.error(f"Database error while loading into {table_name}: {e}")
            raise