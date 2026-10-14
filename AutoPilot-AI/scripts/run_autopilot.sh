#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "========================================================"
echo "  AutoPilot AI - Universal Coding Agent Automation"
echo "========================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.10+."
    exit 1
fi

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
python3 -m autopilot.main "$@"
