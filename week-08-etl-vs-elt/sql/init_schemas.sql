-- Dọn dẹp môi trường thử nghiệm
DROP TABLE IF EXISTS etl_dim_products;
DROP TABLE IF EXISTS elt_raw_products;
DROP TABLE IF EXISTS elt_dim_products;

-- 1. BẢNG ĐÍCH CHO NHÁNH ETL (Chỉ chứa dữ liệu đã sạch do Python đẩy vào)
CREATE TABLE etl_dim_products (
    product_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    original_price NUMERIC(12, 2) NOT NULL,
    discount_pct NUMERIC(5, 2),
    final_price NUMERIC(12, 2) NOT NULL,
    stock_status VARCHAR(20),
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. BẢNG STAGING RAW CHO NHÁNH ELT (Lưu payload JSON thô chưa qua xử lý)
CREATE TABLE elt_raw_products (
    raw_id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. BẢNG ĐÍCH ANALYTICS CHO NHÁNH ELT (Được tạo ra sau khi Database chạy SQL Transform)
CREATE TABLE elt_dim_products (
    product_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    original_price NUMERIC(12, 2) NOT NULL,
    discount_pct NUMERIC(5, 2),
    final_price NUMERIC(12, 2) NOT NULL,
    stock_status VARCHAR(20),
    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);