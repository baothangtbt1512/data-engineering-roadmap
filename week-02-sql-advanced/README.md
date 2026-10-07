# Week 02: Multi-Dimensional E-Commerce Revenue Analytics with SQL

## 1. Objective
Xây dựng pipeline phân tích doanh thu đa chiều (theo ngày, tháng, danh mục sản phẩm, khách hàng, khu vực) từ dữ liệu giao dịch e-commerce; xử lý triệt để bài toán cardinality và row duplication khi JOIN quan hệ 1-N.

## 2. Architecture
[Raw Tables: orders, order_items, customers, products]
│
▼ (Inner Join & Filter status = 'COMPLETED')
[CTE: enriched_sales]
│
┌───────────────┼───────────────┐
▼               ▼               ▼
[Daily/Monthly]   [Product Matrix]  [Region Matrix]


## 3. Technologies
* PostgreSQL / DBeaver
* Git & GitHub

## 4. Dataset
Tập dữ liệu giả lập mô hình thương mại điện tử gồm 4 bảng cốt lõi:
* `customers`: Thông tin khách hàng và vùng miền.
* `products`: Danh mục và đơn giá sản phẩm.
* `orders`: Đơn hàng, ngày đặt và trạng thái giao dịch.
* `order_items`: Chi tiết từng dòng sản phẩm trong đơn, số lượng, chiết khấu.

## 5. Implementation
* **CTE Hierarchy**: Tách bạch bước tính `net_revenue` ở mức dòng sản phẩm (`line_sales`) trước khi ghép dữ liệu header.
* **Join Cardinality**: Sử dụng `INNER JOIN` trên các cặp khóa ngoại hợp lệ để tránh tích Descartes hoặc nhân đôi số dòng khi tính tổng.
* **Aggregations**: Sử dụng `GROUP BY`, `SUM()`, `COUNT(DISTINCT order_id)` và hàm ngày `DATE_TRUNC`.

## 6. Data Pipeline
* `01_init_schema.sql`: Khởi tạo bảng và thiết lập khóa ngoại.
* `02_seed_data.sql`: Nạp mock data để kiểm thử.
* `03_revenue_report.sql`: Các câu truy vấn tổng hợp báo cáo 5 chiều.

## 7. Result
* Tổng hợp thành công doanh thu theo từng tháng và phân bổ theo từng vùng miền.
* Phân loại được danh sách khách hàng chi tiêu nhiều nhất và sản phẩm bán chạy nhất.

## 8. Performance
* Hạn chế subquery lồng nhau bằng cách gom nhóm dữ liệu trong CTE.
* Lọc trạng thái `status = 'COMPLETED'` ngay từ đầu để giảm bớt số dòng cần xử lý.

## 9. Problems & Solutions
* **Vấn đề**: Khi join bảng `orders` (1) và `order_items` (N), nếu tiếp tục join thiếu cẩn thận với bảng thanh toán hoặc khuyến mãi có thể làm sai lệch hàm `SUM()`.
* **Giải pháp**: Tính doanh thu ở mức chi tiết nhất (`order_items`) trước rồi mới aggregate lên các chiều phân tích.

## 10. What I Learned
* Nắm chắc sự khác biệt giữa `INNER JOIN`, `LEFT JOIN` và hiện tượng Row Explosion.
* Cách viết CTE (`WITH ... AS`) tường minh, dễ đọc và dễ mở rộng.

## 11. How to Run
Chạy lần lượt các file trong thư mục `queries/` qua công cụ quản lý cơ sở dữ liệu (DBeaver/pgAdmin/psql):
1. Chạy `01_init_schema.sql`
2. Chạy `02_seed_data.sql`
3. Chạy `03_revenue_report.sql`

## 12. Future Improvements
* Tuần 3: Áp dụng Window Functions (`RANK`, `DENSE_RANK`, `LAG`, `LEAD`) để tính tốc độ tăng trưởng doanh thu so với tháng trước (Month-over-Month).