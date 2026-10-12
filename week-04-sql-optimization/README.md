# Week 04: SQL Performance Lab — Indexing & Execution Plan Optimization

## 1. Objective
Nghiên cứu cơ chế vận hành của PostgreSQL Query Planner trên tập dữ liệu lớn (1,000,000 records); phân tích Execution Plans bằng `EXPLAIN (ANALYZE, BUFFERS)` và áp dụng các kỹ thuật đánh Index (B-Tree, Composite Index, Partial Index) nhằm giảm thiểu thời gian thực thi (Execution Time) và I/O Disk Reads.

## 2. Architecture
[Client Query: Filter / Aggregate]
│
▼
PostgreSQL Cost-Based Optimizer (CBO)
│
┌───────┴───────┐
▼               ▼
[Before: Seq Scan]    [After: Index Scan]

Đọc toàn bộ 1M dòng   - Tra cứu cây B-Tree

Tốn Buffer / I/O      - Truy xuất trực tiếp Block đích


## 3. Technologies
* PostgreSQL 15+
* pgAdmin 4 (Query Tool & Explain Graphical View)
* Git & GitHub

## 4. Dataset
Bảng `large_orders` gồm **1,000,000 dòng** giao dịch thương mại điện tử sinh tự động bằng `generate_series()`:
* Dung lượng bảng: ~65 MB
* Trường dữ liệu: `order_id`, `customer_id`, `order_date`, `status`, `total_amount`.

## 5. Implementation
* **Benchmark 1**: Lọc theo khoảng thời gian (`order_date BETWEEN ...`) để phân tích chuyển dịch từ `Seq Scan` sang `Bitmap Index Scan`.
* **Benchmark 2**: Truy vấn lịch sử khách hàng kết hợp lọc trạng thái và sắp xếp (`WHERE customer_id = ... AND status = ... ORDER BY order_date DESC`). Sử dụng **Composite Index** để triệt tiêu bước Sort trên bộ nhớ (`Sort Method: top-N heapsort` hoặc `quicksort`).
* **Benchmark 3**: Áp dụng **Partial Index** chỉ đánh chỉ mục cho đơn `COMPLETED`, giúp giảm dung lượng Index trên đĩa cứng tới 40%.

## 6. Data Pipeline
* `01_generate_large_dataset.sql`: Script DDL và phát sinh 1M dòng dữ liệu giả lập.
* `02_benchmark_queries.sql`: Bộ test so sánh hiệu năng trước và sau khi đánh chỉ mục.

## 7. Result

### Bảng đối chiếu hiệu năng (Benchmark Results on 1M Rows)

| Kịch bản | Cơ chế quét (Scan Type) | Execution Time (Trước) | Execution Time (Sau) | Mức độ cải thiện | Shared Buffers Read |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Date Range Filter** | Seq Scan ➔ Bitmap Index Scan | **~85.4 ms** | **~6.1 ms** | **Nhanh hơn ~14x** | Giảm từ 8,334 blocks xuống 820 blocks |
| **Customer Order History** | Seq Scan ➔ Index Scan | **~72.8 ms** | **~0.08 ms** | **Nhanh hơn ~900x** | Giảm từ 8,334 blocks xuống 4 blocks |

---

## 8. Performance Deep Dive

### Case Study: Customer Order History
```sql
SELECT order_id, order_date, total_amount
FROM large_orders
WHERE customer_id = 4521 AND status = 'COMPLETED'
ORDER BY order_date DESC;