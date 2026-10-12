-- Tạo bảng đơn hàng lớn riêng biệt để benchmark hiệu năng
CREATE TABLE IF NOT EXISTS large_orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount NUMERIC(12, 2) NOT NULL
);

-- Sinh 1,000,000 dòng giao dịch giả lập trong vòng 3 năm (2024 - 2026)
TRUNCATE TABLE large_orders;

INSERT INTO large_orders (customer_id, order_date, status, total_amount)
SELECT 
    -- 10,000 khách hàng ngẫu nhiên
    (floor(random() * 10000) + 1)::INT AS customer_id,
    
    -- Ngày ngẫu nhiên từ 01/01/2024 đến 31/12/2026
    (DATE '2024-01-01' + (random() * (DATE '2026-12-31' - DATE '2024-01-01'))::INT) AS order_date,
    
    -- Trạng thái ngẫu nhiên theo tỷ lệ
    (ARRAY['COMPLETED', 'COMPLETED', 'COMPLETED', 'CANCELLED', 'REFUNDED'])[floor(random() * 5 + 1)] AS status,
    
    -- Giá trị đơn hàng từ 50,000 đến 5,000,000 VND
    ROUND((50000 + random() * 4950000)::NUMERIC, 2) AS total_amount
FROM generate_series(1, 1000000);

-- Cập nhật thống kê catalog để Query Planner có thông tin chính xác nhất
ANALYZE large_orders;