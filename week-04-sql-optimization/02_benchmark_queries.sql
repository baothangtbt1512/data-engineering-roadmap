-- =========================================================================
-- CASE 1: LỌC THEO KHOẢNG THỜI GIAN & TÍNH TỔNG DOANH THU (B-Tree Index)
-- =========================================================================

-- [A] TRƯỚC KHI TẠO INDEX (Baseline: Sequential Scan)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    DATE_TRUNC('month', order_date)::DATE AS sales_month,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS revenue
FROM large_orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY 1;

-- [B] TẠO B-TREE INDEX TRÊN CỘT NGÀY
CREATE INDEX idx_large_orders_date ON large_orders(order_date);

-- [C] SAU KHI TẠO INDEX (Index Scan / Bitmap Index Scan)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    DATE_TRUNC('month', order_date)::DATE AS sales_month,
    COUNT(*) AS total_orders,
    SUM(total_amount) AS revenue
FROM large_orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-03-31'
GROUP BY 1;


-- =========================================================================
-- CASE 2: TRUY VẤN LỊCH SỬ MUA HÀNG CỦA 1 KHÁCH HÀNG (Composite Index)
-- =========================================================================

-- [A] TRƯỚC KHI TẠO INDEX
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM large_orders
WHERE customer_id = 4521 
  AND status = 'COMPLETED'
ORDER BY order_date DESC;

-- [B] TẠO COMPOSITE INDEX (customer_id + status + order_date)
-- Thứ tự: Cột lọc bằng (=) đặt trước, cột sắp xếp/lọc khoảng đặt sau
CREATE INDEX idx_orders_cust_status_date 
ON large_orders(customer_id, status, order_date DESC);

-- [C] SAU KHI TẠO COMPOSITE INDEX
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM large_orders
WHERE customer_id = 4521 
  AND status = 'COMPLETED'
ORDER BY order_date DESC;


-- =========================================================================
-- CASE 3: TỐI ƯU DUNG LƯỢNG VỚI PARTIAL INDEX
-- (Chỉ đánh index các đơn COMPLETED vì chiếm đa số nghiệp vụ phân tích)
-- =========================================================================

-- Xóa index cũ nếu có
DROP INDEX IF EXISTS idx_orders_cust_status_date;

-- Tạo Partial Index (nhỏ gọn, không tốn ram lưu đơn CANCELLED/REFUNDED)
CREATE INDEX idx_orders_completed_customers 
ON large_orders(customer_id, order_date DESC)
WHERE status = 'COMPLETED';

-- Kiểm tra lại kế hoạch thực thi
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total_amount
FROM large_orders
WHERE customer_id = 4521 
  AND status = 'COMPLETED'
ORDER BY order_date DESC;