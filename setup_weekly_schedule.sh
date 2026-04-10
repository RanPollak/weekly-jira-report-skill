#!/usr/bin/env bash
set -euo pipefail

# Default: Friday 18:00 Israel time.
# Usage:
#   ./setup_weekly_schedule.sh
#   ./setup_weekly_schedule.sh 17:30
RUN_TIME="${1:-18:00}"

if [[ ! "${RUN_TIME}" =~ ^([01]?[0-9]|2[0-3]):[0-5][0-9]$ ]]; then
  echo "Invalid time format: ${RUN_TIME}"
  echo "Use HH:MM in 24-hour format (example: 18:00)"
  exit 1
fi

HOUR="${RUN_TIME%:*}"
MINUTE="${RUN_TIME#*:}"
HOUR=$((10#${HOUR}))
MINUTE=$((10#${MINUTE}))

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="${SCRIPT_DIR}/run_weekly_report.sh"
LOG_FILE="${SCRIPT_DIR}/logs/cron.log"
CRON_TAG="weekly-jira-report"

mkdir -p "${SCRIPT_DIR}/logs"

if [[ ! -x "${RUNNER}" ]]; then
  echo "Runner script is missing or not executable: ${RUNNER}"
  echo "Run: chmod +x \"${RUNNER}\""
  exit 1
fi

TZ_LINE="CRON_TZ=Asia/Jerusalem # ${CRON_TAG}"
ENTRY="${MINUTE} ${HOUR} * * 5 /bin/bash \"${RUNNER}\" >> \"${LOG_FILE}\" 2>&1 # ${CRON_TAG}"
if command -v crontab >/dev/null 2>&1; then
  EXISTING_CRON="$(crontab -l 2>/dev/null || true)"
  FILTERED_CRON="$(printf '%s\n' "${EXISTING_CRON}" | awk -v tag="${CRON_TAG}" 'index($0, tag)==0' || true)"

  {
    printf '%s\n' "${FILTERED_CRON}"
    printf '%s\n' "${TZ_LINE}"
    printf '%s\n' "${ENTRY}"
  } | awk 'NF' | crontab -

  echo "Weekly schedule installed via crontab."
  echo "Runs every Friday at $(printf '%02d:%02d' "${HOUR}" "${MINUTE}") Israel time (Asia/Jerusalem)."
  echo "Verify with: crontab -l | awk '/weekly-jira-report/'"
  exit 0
fi

# Fallback for systems without crontab: systemd user timer
if command -v systemctl >/dev/null 2>&1; then
  UNIT_DIR="${HOME}/.config/systemd/user"
  SERVICE_FILE="${UNIT_DIR}/weekly-jira-report.service"
  TIMER_FILE="${UNIT_DIR}/weekly-jira-report.timer"
  mkdir -p "${UNIT_DIR}"

  cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Weekly Jira Report Runner

[Service]
Type=oneshot
ExecStart=/bin/bash ${RUNNER}
EOF

  cat > "${TIMER_FILE}" <<EOF
[Unit]
Description=Run Weekly Jira Report (Friday Israel time)

[Timer]
OnCalendar=Fri *-*-* $(printf '%02d:%02d' "${HOUR}" "${MINUTE}"):00 Asia/Jerusalem
Persistent=true
Unit=weekly-jira-report.service

[Install]
WantedBy=timers.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now weekly-jira-report.timer

  echo "Weekly schedule installed via systemd user timer."
  echo "Runs every Friday at $(printf '%02d:%02d' "${HOUR}" "${MINUTE}") Israel time (Asia/Jerusalem)."
  echo "Verify with: systemctl --user status weekly-jira-report.timer"
  exit 0
fi

echo "Could not install schedule automatically."
echo "Neither 'crontab' nor 'systemctl' is available on this machine."
exit 1
