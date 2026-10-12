import os
import sys
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

def load_data():
    input_file = "data/transformed_data.json"
    if not os.path.exists(input_file):
        print(f"[LOAD ERROR] Transformed data missing: {input_file}", file=sys.stderr)
        sys.exit(1)

    # Đọc cấu hình kết nối linh hoạt
    conn_params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
        "dbname": os.getenv("DB_NAME", "ecommerce_analytics"),
        "user": os.getenv("DB_USER", "postgres")
    }
    password = os.getenv("DB_PASSWORD", "").strip()
    if password:
        conn_params["password"] = password

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            records = json.load(f)

        tuples = [
            (
                r["product_id"],
                r["title"],
                r["category"],
                r["original_price"],
                r["discount_percentage"],
                r["net_price"],
                r["stock"]
            )
            for r in records
        ]

        query = """
            INSERT INTO daily_product_snapshots 
            (product_id, title, category, original_price, discount_percentage, net_price, stock, snapshot_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
            ON CONFLICT (product_id, snapshot_date) DO UPDATE SET
                title = EXCLUDED.title,
                original_price = EXCLUDED.original_price,
                discount_percentage = EXCLUDED.discount_percentage,
                net_price = EXCLUDED.net_price,
                stock = EXCLUDED.stock;
        """

        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # Tạo bảng nếu chưa có
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS daily_product_snapshots (
                        product_id INT NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        category VARCHAR(100),
                        original_price NUMERIC(12, 2) NOT NULL,
                        discount_percentage NUMERIC(5, 2),
                        net_price NUMERIC(12, 2) NOT NULL,
                        stock INT,
                        snapshot_date DATE NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (product_id, snapshot_date)
                    );
                """)
                execute_batch(cur, query, tuples, page_size=100)
            conn.commit()

        print(f"[LOAD] Successfully upserted {len(tuples)} daily snapshots to PostgreSQL.")
        sys.exit(0)
    except Exception as e:
        print(f"[LOAD ERROR] Database loading failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    load_data()