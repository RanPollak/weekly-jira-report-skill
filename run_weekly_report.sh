#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOCK_FILE="/tmp/weekly-jira-report.lock"

mkdir -p "${LOG_DIR}"

DATE_STAMP="$(date +%Y-%m-%d)"
TIME_STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
LOG_FILE="${LOG_DIR}/weekly_report_${DATE_STAMP}.log"

exec 200>"${LOCK_FILE}"
if ! flock -n 200; then
  echo "[${TIME_STAMP}] Another weekly report run is in progress. Exiting." >> "${LOG_FILE}"
  exit 1
fi

{
  echo "=================================================="
  echo "[${TIME_STAMP}] Starting weekly Jira report pipeline"
  echo "=================================================="

  python3 "${SCRIPT_DIR}/generate_weekly_update.py"
  python3 "${SCRIPT_DIR}/convert_update_to_html.py"

  echo "[${TIME_STAMP}] Weekly Jira report pipeline finished successfully"
} >> "${LOG_FILE}" 2>&1
