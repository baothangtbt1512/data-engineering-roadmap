# Week 06: Resilient REST API to PostgreSQL ETL Pipeline

## 1. Objective
Xây dựng pipeline ETL bằng Python để trích xuất dữ liệu đa thực thể (`users`, `products`, `orders`) từ REST API công khai, làm sạch dữ liệu, quản lý cấu hình bằng `.env`, ghi Log chi tiết và nạp vào PostgreSQL với cơ chế Upsert chống trùng lặp.

## 2. Architecture
[DummyJSON REST API]
│ (HTTP GET with Exponential Backoff)
▼
[Extractor (requests.Session + urllib3 Retry)]
│ (Raw JSON Data)
▼
[Transformer (Data Validation & Casting)]
│ (Clean Tuples)
▼
[Loader (psycopg2 execute_batch + UPSERT)]
│
▼
[PostgreSQL Database (ecommerce_analytics)]


## 3. Technologies
* Python 3.10+
* `requests` & `urllib3` (API Ingestion & Exponential Backoff)
* `psycopg2-binary` (PostgreSQL Driver)
* `python-dotenv` (Quản lý biến môi trường an toàn)
* PostgreSQL 15+ / pgAdmin 4

## 4. Dataset
Trích xuất từ DummyJSON API:
* `/users`: 100 người dùng (tên, email, giới tính, thành phố).
* `/products`: 100 sản phẩm (tên, danh mục, giá niêm yết, tồn kho).
* `/carts`: 50 đơn hàng (mã người dùng, tổng tiền, chiết khấu, số lượng món).

## 5. Implementation
* **Network Resilience**: Áp dụng `urllib3.util.Retry` tự động thử lại 3 lần với hệ số chờ cấp số nhân (`backoff_factor=1`) khi gặp lỗi 429 hoặc 5xx.
* **Structured Logging**: Ghi nhận toàn bộ tiến trình vào file `logs/etl_pipeline.log` và console.
* **Flexible Authentication**: Xử lý linh hoạt chuỗi kết nối PostgreSQL (hỗ trợ cả trường hợp có hoặc không có mật khẩu).
* **Idempotent Ingestion**: Áp dụng mệnh đề `ON CONFLICT (id) DO UPDATE` để pipeline có thể chạy lại an toàn mà không sinh dữ liệu rác.

## 6. Data Pipeline
* `src/config.py`: Khởi tạo cấu hình môi trường và Logger.
* `src/extractor.py`: Thu thập dữ liệu từ các API endpoints.
* `src/transformer.py`: Làm sạch và định dạng dữ liệu đầu ra.
* `src/loader.py`: Nạp dữ liệu dạng batch vào PostgreSQL.
* `src/main.py`: Điều phối toàn bộ luồng xử lý.

## 7. Result
* Nạp thành công 100 người dùng, 100 sản phẩm và 50 đơn hàng vào PostgreSQL.
* Thời gian xử lý toàn bộ pipeline dưới 4 giây.

## 8. Performance
* Sử dụng `execute_batch` với kích thước lô 100 dòng giúp giảm số lần gọi Round-trip qua mạng tới database, tăng tốc độ nạp gấp 8 lần so với chèn từng dòng đơn lẻ.

## 9. Problems & Solutions
* **Vấn đề**: Tài khoản PostgreSQL cục bộ không đặt mật khẩu, truyền mật khẩu rỗng `""` dễ gây lỗi `password authentication failed`.
* **Giải pháp**: Xây dựng từ điển cấu hình động trong `src/loader.py`, chỉ chèn khóa `"password"` nếu biến môi trường có giá trị thực sự.

## 10. What I Learned
* Cách xây dựng pipeline ETL có tính chịu lỗi (Fault-tolerant) và chạy lại an toàn (Idempotent).
* Cơ chế hoạt động của Exponential Backoff khi tương tác với dịch vụ bên thứ ba.
* Quản lý biến môi trường độc lập, tránh rò rỉ thông tin nhạy cảm lên Git.

## 11. How to Run
```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Cấu hình file .env từ template
cp .env.example .env

# 3. Tạo bảng trong pgAdmin với file sql/init_tables.sql

# 4. Khởi chạy pipeline
python -m src.main