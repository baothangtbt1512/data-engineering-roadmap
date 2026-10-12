# Week 08: Architectural & Performance Deep Dive — ETL vs ELT Comparison

## 1. Objective
Nghiên cứu thực nghiệm sự khác biệt cốt lõi giữa hai triết lý kiến trúc dữ liệu: **ETL (Extract - Transform - Load)** và **ELT (Extract - Load - Transform)** trên cùng một tập dữ liệu 50,000 dòng. Đo lường định lượng các chỉ số: thời gian thực thi (Execution Time), tiêu thụ bộ nhớ (RAM consumption), độ phức tạp mã nguồn (Maintainability) và khả năng mở rộng khi khối lượng dữ liệu phình to (Scalability).

## 2. Architecture Comparison

### Pipeline A: Truyền thống (ETL Pattern)
[External Source] ──> [Python Memory Engine] ──> [Clean Production Table]
(Extract)             (Transform: CPU/RAM)            (Load Final)

* **Đặc tính**: Dữ liệu thô bị hủy bỏ sau xử lý; Database chỉ thấy dữ liệu đã được làm sạch hoàn chỉnh.

### Pipeline B: Hiện đại (ELT Pattern)
[External Source] ──> [Staging Raw Table (JSONB)] ──> [Analytics Table]
(Extract)                  (Load Raw)               (SQL Transform Engine)

* **Đặc tính**: Giữ lại toàn bộ dấu vết dữ liệu thô (Data Lineage/Auditability); tận dụng sức mạnh tính toán song song nội tại của Database Engine.

## 3. Technologies
* Python 3.10+ (`psycopg2-binary`, `psutil`)
* PostgreSQL 15+ (với kiểu dữ liệu `JSONB` và truy vấn bán cấu trúc)
* Git & GitHub

## 4. Dataset
Tập dữ liệu giả lập thương mại điện tử gồm **50,000 records**:
* Mỗi bản ghi chứa: `id`, `title`, `category`, `price`, `discountPercentage`, `stock`.
* Dữ liệu đầu vào cố tình chứa khoảng trắng thừa, chữ hoa/thường không chuẩn để kiểm thử tầng transform.

## 5. Implementation
* **ETL Pipeline**: Thực hiện bóc tách, ép kiểu, làm sạch chuỗi và tính toán `final_price`, `stock_status` hoàn toàn bằng cấu trúc dữ liệu nguyên bản của Python trong bộ nhớ trước khi nạp batch vào PostgreSQL.
* **ELT Pipeline**: Sử dụng `json.dumps()` nạp trực tiếp toàn bộ object vào cột `JSONB` của bảng `elt_raw_products`. Sau đó gọi một câu lệnh `INSERT INTO ... SELECT` để database tự bóc tách bằng toán tử `->>` và `CASE WHEN`.

## 6. Data Pipeline
* `src/pipeline_etl.py`: Triển khai kiến trúc ETL.
* `src/pipeline_elt.py`: Triển khai kiến trúc ELT.
* `src/benchmark_runner.py`: Bộ điều phối benchmark đo lường bộ nhớ và thời gian thực thi.
* `sql/init_schemas.sql`: DDL cho cả 2 luồng.

## 7. Result

### Bảng kết quả thực nghiệm (Benchmark trên 50,000 records)

| Tiêu chí so sánh | Pipeline A (ETL) | Pipeline B (ELT) | Đánh giá kiến trúc |
| :--- | :--- | :--- | :--- |
| **Transform Engine** | Python (Application Node) | PostgreSQL Engine | ELT tận dụng bộ tối ưu CBO của DB |
| **Thời gian Transform** | ~0.18 giây | ~0.35 giây | Python xử lý đơn giản in-memory nhanh |
| **Thời gian Load** | ~2.95 giây | ~3.12 giây | ELT tốn thêm dung lượng ghi JSONB |
| **TỔNG THỜI GIAN** | **~3.13 giây** | **~3.47 giây** | Ngang ngửa trên scale nhỏ |
| **RAM Python chiếm dụng** | **~35 - 45 MB** | **< 10 MB** | **ELT vượt trội về quản lý bộ nhớ** |
| **Khả năng tái xử lý (Replay)** | **Không thể** (mất raw data) | **Dễ dàng** (raw JSONB còn nguyên) | **ELT thắng tuyệt đối** |

---

## 8. Phân tích 4 khía cạnh chuyên sâu (4 Evaluation Pillars)

### 1. Architecture (Kiến trúc hệ thống)
* **ETL**: Tách rời tầng tính toán khỏi Database. Tốt khi database đích là hệ thống OLTP có tài nguyên CPU hạn chế, hoặc khi dữ liệu nguồn chứa thông tin nhạy cảm (PII, thẻ ngân hàng) bắt buộc phải ẩn đi trước khi lưu kho.
* **ELT**: Coi Database/Data Warehouse là trung tâm tính toán. Tách bạch hoàn toàn trách nhiệm của Data Ingestion (chỉ lo trích xuất và nạp) và Data Modeling (chuyên viên phân tích/analytics engineer dùng SQL để transform).

### 2. Performance (Hiệu năng)
* Trên tập dữ liệu nhỏ (< 500,000 dòng), Python xử lý vòng lặp trên RAM có thể nhanh hơn do không tốn chi phí parse JSONB của Database.
* Tuy nhiên, trên tập dữ liệu lớn (hàng triệu dòng), **ELT thắng thế** vì các Data Warehouse hiện đại (ClickHouse, BigQuery, Snowflake) hỗ trợ tính toán phân tán (Massively Parallel Processing - MPP) và lưu trữ theo cột (Columnar Storage), vượt xa khả năng xử lý đơn luồng của một worker Python.

### 3. Maintainability (Khả năng bảo trì & Thay đổi nghiệp vụ)
* **ETL**: Nếu nghiệp vụ thay đổi công thức tính (ví dụ: đổi ngưỡng `LOW_STOCK` từ 10 thành 20), ta buộc phải **chạy lại toàn bộ quá trình Extract từ API nguồn**. Nếu API nguồn không cho phép lấy lại dữ liệu cũ, pipeline bị gãy.
* **ELT**: Toàn bộ dữ liệu thô còn nguyên trong bảng Staging (`JSONB`). Khi nghiệp vụ thay đổi, ta chỉ cần sửa lại câu lệnh SQL và chạy `TRUNCATE` rồi `INSERT` lại bảng `dim` trong vài giây mà không cần gọi lại API nguồn.

### 4. Scalability (Khả năng mở rộng)
* **ETL**: Scale-up theo phương thẳng đứng (Vertical Scaling) của máy chủ chạy Python (cần thêm RAM để không bị lỗi `Out Of Memory` khi dữ liệu tăng).
* **ELT**: Scale-out theo năng lực của Database Cluster. Lưu trữ rẻ (S3, GCS, Staging table) cho phép nạp dữ liệu không giới hạn, việc biến đổi có thể thực hiện theo lô hoặc theo nhu cầu truy vấn.

## 9. Problems & Solutions
* **Vấn đề**: Nhánh ELT ghi dữ liệu JSONB làm tăng dung lượng lưu trữ trên đĩa cứng của PostgreSQL.
* **Giải pháp**: Thiết lập chính sách xoay vòng (Retention Policy/TTL): Dữ liệu trong bảng `elt_raw_products` chỉ lưu trong 30-90 ngày để phục vụ audit/re-transform, sau đó tự động nén hoặc chuyển sang lưu trữ dạng Cold Storage (MinIO/S3).

## 10. What I Learned
* Hiểu sâu lý do các công cụ hiện đại như **dbt, Airbyte, Fivetran** thúc đẩy sự dịch chuyển toàn ngành từ ETL sang ELT.
* Kiểu dữ liệu `JSONB` trong PostgreSQL là công cụ cầu nối trung gian tuyệt vời giữa cấu trúc Schema-on-Read và Schema-on-Write.
* Tư duy chọn kiến trúc: Không có giải pháp nào tốt nhất mọi trường hợp, chỉ có giải pháp phù hợp với chi phí phần cứng và bài toán nghiệp vụ.

## 11. How to Run
```bash
# 1. Tạo schemas trong database
psql -h localhost -U postgres -d ecommerce_analytics -f sql/init_schemas.sql

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Chạy benchmark so sánh
python -m src.benchmark_runner