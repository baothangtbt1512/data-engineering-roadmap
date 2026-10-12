#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PIPELINE_SCRIPT="$PROJECT_ROOT/scripts/run_pipeline.sh"

# Cấp quyền thực thi
chmod +x "$PIPELINE_SCRIPT"

# Dòng lệnh cron chạy vào lúc 01:00 mỗi sáng
CRON_JOB="0 1 * * * /bin/bash $PIPELINE_SCRIPT >> $PROJECT_ROOT/logs/cron_system.log 2>&1"

# Kiểm tra nếu job chưa có trong crontab thì thêm vào
(crontab -l 2>/dev/null | grep -Fv "$PIPELINE_SCRIPT" ; echo "$CRON_JOB") | crontab -

echo "[SUCCESS] Crontab updated successfully!"
echo "Current crontab entries:"
crontab -l