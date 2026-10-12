# Week 03: Customer Ranking & Sales Trends Analytics

## 1. Objective
Ứng dụng các hàm cửa sổ (Window Functions) nâng cao trong PostgreSQL để giải quyết các bài toán phân tích xu hướng chuỗi thời gian (MoM Growth, Running Total) và bài toán Top-N theo phân vùng (Partitioning) mà không làm suy giảm hiệu năng do self-join.

## 2. Architecture
[Raw Tables: orders, order_items, customers, products]
│
▼ (Aggregate by Time / Dimension)
[Base CTE: Aggregated Metrics]
│
┌────────────────┴────────────────┐
▼                                 ▼
[Time-Series Windowing]            [Ranking Windowing]

SUM() OVER (ORDER BY date)       - DENSE_RANK() OVER (PARTITION BY month)

LAG() OVER (ORDER BY date)       - ROW_NUMBER() OVER (PARTITION BY category)


## 3. Technologies
* PostgreSQL 15+ / pgAdmin 4
* Git & GitHub

## 4. Dataset
Tập dữ liệu mở rộng từ Tuần 2 với các giao dịch trải dài từ Tháng 01/2026 đến Tháng 04/2026 để kiểm thử phân tích chuỗi thời gian (Time-series).

## 5. Implementation
* **Time-Series Analysis**:
  * Sử dụng `SUM(...) OVER (ORDER BY sales_month)` tính tổng tích lũy (Running Total).
  * Sử dụng `LAG(current_revenue, 1) OVER (ORDER BY sales_month)` lấy giá trị kỳ trước để tính chênh lệch tuyệt đối và % tăng trưởng MoM.
  * Xử lý trường hợp chia cho 0 bằng hàm `NULLIF()`.
* **Top-N Partitioning**:
  * Dùng `DENSE_RANK()` phân hạng Top khách hàng chi tiêu theo từng tháng (`PARTITION BY sales_month`).
  * Dùng `ROW_NUMBER()` để lọc chính xác sản phẩm có doanh thu cao nhất theo từng danh mục (`PARTITION BY category`).

## 6. Data Pipeline
* `01_additional_seed_data.sql`: Bổ sung dữ liệu đa tháng.
* `02_window_analysis.sql`: Kịch bản phân tích Top-N và tăng trưởng MoM.

## 7. Result
Bảng tính toán tăng trưởng doanh thu theo tháng (MoM Growth):
| sales_month | current_revenue | running_total_revenue | prev_month_revenue | revenue_diff | mom_growth_pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-01-01 | 2,500,000.00 | 2,500,000.00 | NULL | NULL | NULL |
| 2026-02-01 | 4,550,000.00 | 7,050,000.00 | 2,500,000.00 | +2,050,000.00 | +82.00% |
| 2026-03-01 | 8,437,500.00 | 15,487,500.00| 4,550,000.00 | +3,887,500.00 | +85.44% |

## 8. Performance
* So với việc tự join lại chính bảng đó (`Self-Join`) để tìm tháng trước, `LAG()` chỉ duyệt qua tập dữ liệu 1 lần, giảm độ phức tạp tính toán từ $O(N^2)$ xuống $O(N \log N)$ (do chỉ tốn chi phí Sort).

## 9. Problems & Solutions
* **Vấn đề**: Tháng đầu tiên trong chuỗi không có tháng trước đó (`LAG` trả về `NULL`), dẫn đến công thức tính `% MoM` bị `NULL` hoặc lỗi chia cho 0 nếu mẫu số là 0.
* **Giải pháp**: Bọc mẫu số bằng `NULLIF(LAG(...), 0)` để tránh lỗi runtime chia cho 0 (Division by zero error).

## 10. What I Learned
* Phân biệt rõ sự khác nhau giữa:
  * `ROW_NUMBER()`: Đánh số thứ tự duy nhất, không trùng lặp.
  * `RANK()`: Đồng hạng thì chung số, nhưng nhảy cóc số thứ tự tiếp theo (1, 2, 2, 4).
  * `DENSE_RANK()`: Đồng hạng thì chung số, không nhảy cóc số tiếp theo (1, 2, 2, 3).
* Nắm vững cơ chế vận hành của mệnh đề `PARTITION BY` và khung cửa sổ trượt (Frame Specification: `ROWS BETWEEN ...`).

## 11. How to Run
Mở Query Tool trên pgAdmin 4:
1. Chạy `01_additional_seed_data.sql` để nạp dữ liệu chuỗi thời gian.
2. Mở và chạy `02_window_analysis.sql` để kiểm tra kết quả các chỉ số.

## 12. Future Improvements
* Tuần 4: Đo lường và tối ưu hóa hiệu năng bằng `EXPLAIN ANALYZE`, đánh Index trên các cột thường xuyên dùng trong `PARTITION BY` và `ORDER BY`.