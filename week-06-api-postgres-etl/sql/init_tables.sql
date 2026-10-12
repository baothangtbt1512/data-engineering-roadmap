-- 1. Bảng Users lấy từ API
CREATE TABLE IF NOT EXISTS api_users (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Products lấy từ API
CREATE TABLE IF NOT EXISTS api_products (
    product_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price NUMERIC(12, 2) NOT NULL,
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Orders lấy từ API
CREATE TABLE IF NOT EXISTS api_orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    total_products INT,
    total_quantity INT,
    total_amount NUMERIC(12, 2) NOT NULL,
    discounted_total NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);