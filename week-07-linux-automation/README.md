# Week 07: Automated End-to-End Data Pipeline with Bash & Cron

## 1. Objective
Tự động hóa hoàn toàn quy trình thực thi Data Pipeline hàng ngày (Daily Ingestion) bằng Bash Shell script và lập lịch Linux Crontab; tích hợp cơ chế bắt lỗi nghiêm ngặt (Trap Error Handling), kiểm soát Exit Code giữa các công đoạn và dọn dẹp bộ nhớ tạm (Housekeeping).

## 2. Pipeline Architecture
[Linux Crontab (01:00 AM Daily)]
│
▼
[scripts/run_pipeline.sh] (Orchestrator: set -euo pipefail)
│
┌──────────┴──────────┐
▼                     ▼ (If Error)
[src/extract.py]    ──> [Trap Handler -> Abort Pipeline -> Alert Log]
│ (Exit 0)
▼
[src/transform.py]  ──> [Trap Handler -> Abort Pipeline -> Alert Log]
│ (Exit 0)
▼
[src/load.py]       ──> [Trap Handler -> Abort Pipeline -> Alert Log]
│ (Exit 0)
▼
[PostgreSQL Table: daily_product_snapshots (UPSERT)]
│
▼
[Housekeeping: Clean temp files & Archive logs]


## 3. Technologies
* Linux / WSL (Ubuntu) / Bash Shell
* Cron (Daemon Scheduler)
* Python 3.10+ (Module ETL độc lập)
* PostgreSQL 15+ / pgAdmin 4
* Git & GitHub

## 4. Dataset
Daily Product Snapshots trích xuất từ DummyJSON API:
* Dữ liệu thời giá thực tế (Price, Discount Percentage, Net Price, Stock) được lưu kèm nhãn thời gian `snapshot_date = CURRENT_DATE`.

## 5. Implementation
* **Decoupled Architecture**: Tách biệt hoàn toàn `extract.py`, `transform.py`, và `load.py` thành các process độc lập trả về Linux Exit Code tiêu chuẩn (`0` = OK, `1` = Error).
* **Defensive Bash Scripting**: Sử dụng cờ `set -euo pipefail` cùng cơ chế `trap 'handle_error $LINENO' ERR` để ngăn chặn hiện tượng script tiếp tục chạy khi module phía trước đã sập.
* **Cron Headless Execution**: Quản lý đường dẫn tuyệt đối (`PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"`) để pipeline chạy mượt mà ngay cả khi Cron Daemon gọi script từ bất kỳ thư mục nào trong hệ thống.
* **Idempotent Snapshot Ingestion**: Khóa chính hỗn hợp `PRIMARY KEY (product_id, snapshot_date)` bảo đảm nạp lại trong cùng một ngày sẽ cập nhật chỉ số chứ không trùng bản ghi.

## 6. Data Pipeline
* `scripts/run_pipeline.sh`: Bộ điều phối chính toàn bộ vòng đời pipeline.
* `scripts/cron_setup.sh`: Script tự động thêm lịch vào daemon crontab của OS.
* `src/extract.py`: Trích xuất dữ liệu REST API sang `data/raw_extracted.json`.
* `src/transform.py`: Làm sạch, tính chiết khấu ròng và xuất `data/transformed_data.json`.
* `src/load.py`: Nạp dữ liệu vào bảng `daily_product_snapshots` trong PostgreSQL.

## 7. Result
* Cron kích hoạt chính xác vào lúc 01:00 AM hàng ngày.
* Log được lưu trữ riêng biệt theo từng phiên chạy: `logs/pipeline_YYYY-MM-DD_HH-MM-SS.log`.
* Bảng `daily_product_snapshots` tích lũy lịch sử biến động giá qua từng ngày phục vụ phân tích xu hướng.

## 8. Performance
* Toàn bộ tiến trình chạy trong khoảng ~2.8 giây.
* Dữ liệu trung gian được dọn sạch ngay sau phiên chạy, giúp tiết kiệm dung lượng lưu trữ trên máy chủ.

## 9. Failure Handling
* **Lỗi API down / Mạng chập chờn**: `extract.py` văng Exception và trả về Exit Code `1`.
* **Phản ứng của Bash**: Lệnh `trap ERR` bắt tín hiệu ngay lập tức, ghi dòng code gây lỗi vào log, dừng toàn bộ pipeline và **không kích hoạt `transform.py` hay `load.py`**, bảo vệ database khỏi tình trạng nhận dữ liệu rác/rỗng.

## 10. What I Learned
* Sự khác biệt cốt lõi giữa tương tác thủ công trên terminal và môi trường chạy tự động của Cron (mất $PATH, biến môi trường bị cô lập).
* Triết lý Unix: "Fail Fast, Fail Loudly" với các cờ `set -e` và Exit Code.
* Kỹ thuật thiết kế pipeline nhiều chặng decoupled chuẩn bị nền tảng trước khi chuyển đổi lên DAG của Airflow.

## 11. How to Run
```bash
# 1. Cấp quyền chạy script trên Linux/WSL
chmod +x scripts/run_pipeline.sh scripts/cron_setup.sh

# 2. Chạy thử thủ công pipeline
./scripts/run_pipeline.sh

# 3. Đăng ký lịch chạy tự động lúc 01:00 AM mỗi ngày
./scripts/cron_setup.sh