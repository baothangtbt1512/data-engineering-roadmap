import time
import json
from psycopg2.extras import execute_batch
from src.config import get_db_connection

def run_elt_pipeline(mock_records):
    """
    EXTRACT: mock_records
    LOAD: Nạp nguyên vẹn Payload JSON thô vào bảng staging elt_raw_products
    TRANSFORM: Thực thi SQL script để Database Engine tự parse JSON và aggregate
    """
    t_start = time.perf_counter()

    # --- 1. LOAD RAW (Fast Batch Append into Staging) ---
    t_load_start = time.perf_counter()
    raw_tuples = [(json.dumps(r),) for r in mock_records]
    
    insert_raw_query = "INSERT INTO elt_raw_products (payload) VALUES (%s);"

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE elt_raw_products; TRUNCATE TABLE elt_dim_products;")
            execute_batch(cur, insert_raw_query, raw_tuples, page_size=1000)
        conn.commit()
    t_load = time.perf_counter() - t_load_start

    # --- 2. TRANSFORM (Database-native SQL Engine) ---
    t_trans_start = time.perf_counter()
    sql_transform_query = """
        INSERT INTO elt_dim_products (product_id, title, category, original_price, discount_pct, final_price, stock_status)
        SELECT 
            (payload->>'id')::INT AS product_id,
            TRIM(payload->>'title') AS title,
            LOWER(TRIM(COALESCE(payload->>'category', 'General'))) AS category,
            ROUND((payload->>'price')::NUMERIC, 2) AS original_price,
            ROUND((payload->>'discountPercentage')::NUMERIC, 2) AS discount_pct,
            ROUND(
                ((payload->>'price')::NUMERIC * (1 - (payload->>'discountPercentage')::NUMERIC / 100)), 
                2
            ) AS final_price,
            CASE 
                WHEN (payload->>'stock')::INT <= 0 THEN 'OUT_OF_STOCK'
                WHEN (payload->>'stock')::INT < 10 THEN 'LOW_STOCK'
                ELSE 'IN_STOCK'
            END AS stock_status
        FROM elt_raw_products
        ON CONFLICT (product_id) DO NOTHING;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_transform_query)
        conn.commit()
    t_transform = time.perf_counter() - t_trans_start

    total_time = time.perf_counter() - t_start
    return {
        "pipeline": "ELT",
        "load_time_sec": round(t_load, 4),
        "transform_time_sec": round(t_transform, 4),
        "total_time_sec": round(total_time, 4),
        "rows_processed": len(mock_records)
    }