-- Bổ sung đơn hàng cho Tháng 1, Tháng 2, Tháng 3 năm 2026
INSERT INTO orders (customer_id, order_date, status) VALUES
(1, '2026-01-15', 'COMPLETED'),
(2, '2026-01-20', 'COMPLETED'),
(3, '2026-02-10', 'COMPLETED'),
(4, '2026-02-18', 'COMPLETED'),
(2, '2026-03-10', 'COMPLETED');

-- Chi tiết đơn hàng tương ứng
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount) VALUES
(6, 1, 1, 1500000, 0.00),  -- Order 6 (T1): 1,500,000
(7, 2, 2, 500000, 0.00),   -- Order 7 (T1): 1,000,000 -> Tổng T1 = 2,500,000
(8, 4, 1, 3200000, 0.00),  -- Order 8 (T2): 3,200,000
(9, 1, 1, 1500000, 0.10),  -- Order 9 (T2): 1,350,000 -> Tổng T2 = 4,550,000
(10, 4, 2, 3200000, 0.05); -- Order 10 (T3): 6,080,000