import time
from psycopg2.extras import execute_batch
from src.config import get_db_connection

def run_etl_pipeline(mock_records):
    """
    EXTRACT: mock_records (đã có trong bộ nhớ)
    TRANSFORM: Python CPU & RAM thực thi làm sạch và tính toán
    LOAD: Nạp thẳng bảng sạch etl_dim_products
    """
    t_start = time.perf_counter()

    # --- 1. TRANSFORM (In-Memory Python Processing) ---
    t_trans_start = time.perf_counter()
    transformed_data = []
    for item in mock_records:
        prod_id = int(item["id"])
        title = str(item.get("title", "")).strip()
        category = str(item.get("category", "General")).strip().lower()
        price = round(float(item.get("price", 0.0)), 2)
        discount = round(float(item.get("discountPercentage", 0.0)), 2)
        
        # Business logic transform
        final_price = round(price * (1 - discount / 100), 2)
        stock = int(item.get("stock", 0))
        stock_status = "OUT_OF_STOCK" if stock <= 0 else ("LOW_STOCK" if stock < 10 else "IN_STOCK")

        transformed_data.append((prod_id, title, category, price, discount, final_price, stock_status))
    t_transform = time.perf_counter() - t_trans_start

    # --- 2. LOAD (Database Batch Ingestion) ---
    t_load_start = time.perf_counter()
    insert_query = """
        INSERT INTO etl_dim_products 
        (product_id, title, category, original_price, discount_pct, final_price, stock_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE etl_dim_products;")
            execute_batch(cur, insert_query, transformed_data, page_size=1000)
        conn.commit()
    t_load = time.perf_counter() - t_load_start

    total_time = time.perf_counter() - t_start
    return {
        "pipeline": "ETL",
        "transform_time_sec": round(t_transform, 4),
        "load_time_sec": round(t_load, 4),
        "total_time_sec": round(total_time, 4),
        "rows_processed": len(transformed_data)
    }