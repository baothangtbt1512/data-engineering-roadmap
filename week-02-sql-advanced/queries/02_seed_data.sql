-- Dữ liệu mẫu (Mock data)
INSERT INTO customers (customer_name, region) VALUES
('Nguyễn Văn An', 'Miền Bắc'),
('Trần Thị Bình', 'Miền Nam'),
('Lê Hoàng Cường', 'Miền Trung'),
('Phạm Thị Dung', 'Miền Bắc');

INSERT INTO products (product_name, category, price) VALUES
('Bàn phím cơ', 'Electronics', 1500000),
('Chuột không dây', 'Electronics', 500000),
('Sách Data Engineering', 'Books', 250000),
('Ghế công thái học', 'Furniture', 3200000);

INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2026-03-01', 'COMPLETED'),
(2, '2026-03-02', 'COMPLETED'),
(1, '2026-03-15', 'COMPLETED'),
(3, '2026-03-20', 'CANCELLED'),
(4, '2026-04-05', 'COMPLETED');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES
(1, 1, 1, 1500000, 0.10),
(1, 2, 2, 500000, 0.00),
(2, 3, 3, 250000, 0.05),
(3, 4, 1, 3200000, 0.00),
(4, 2, 1, 500000, 0.00),
(5, 1, 2, 1500000, 0.15);