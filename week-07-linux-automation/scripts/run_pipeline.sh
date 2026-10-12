#!/usr/bin/env bash

# ==============================================================================
# Pipeline Orchestrator: Automated Daily ETL
# Strict mode: -e (exit on error), -u (exit on unset variable), -o pipefail
# ==============================================================================
set -euo pipefail

# Lấy thư mục gốc của project (chống lỗi khi cron gọi từ vị trí khác)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

TIMESTAMP=$(date "+%Y-%m-%d_%H-%M-%S")
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/pipeline_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_ROOT/data"

# Hàm thông báo khi lỗi xảy ra
handle_error() {
    local exit_code=$?
    local line_no=$1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [CRITICAL] Pipeline crashed at line $line_no with exit code $exit_code!" | tee -a "$LOG_FILE"
    # Có thể mở rộng tích hợp gửi cảnh báo Webhook Discord/Slack/Telegram tại đây
    exit "$exit_code"
}

trap 'handle_error $LINENO' ERR

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================================="
log "STARTING DAILY AUTOMATED DATA PIPELINE"
log "Project Directory: $PROJECT_ROOT"
log "=========================================================="

# 1. Kích hoạt môi trường Python (virtualenv nếu có, fallback về python3 hệ thống)
if [ -d "$PROJECT_ROOT/venv" ]; then
    log "[ENV] Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# 2. Stage 1: EXTRACT
log "[STAGE 1/3] Running extract.py..."
python3 src/extract.py 2>&1 | tee -a "$LOG_FILE"

# 3. Stage 2: TRANSFORM
log "[STAGE 2/3] Running transform.py..."
python3 src/transform.py 2>&1 | tee -a "$LOG_FILE"

# 4. Stage 3: LOAD
log "[STAGE 3/3] Running load.py..."
python3 src/load.py 2>&1 | tee -a "$LOG_FILE"

# 5. Dọn dẹp dữ liệu tạm (Housekeeping)
log "[HOUSEKEEPING] Cleaning temporary staging JSON files..."
rm -f "$PROJECT_ROOT/data/raw_extracted.json"
rm -f "$PROJECT_ROOT/data/transformed_data.json"

log "=========================================================="
log "PIPELINE COMPLETED SUCCESSFULLY"
log "=========================================================="
exit 0