#!/bin/bash
set -e
if [[ -z "$1" ]]; then
  echo "Usage: $0 <backup-folder>"
  exit 1
fi
BK="$1"
if [[ ! -f "$BK/workspace.tar.gz" ]]; then
  echo "Backup archive not found: $BK/workspace.tar.gz"
  exit 1
fi
cd /app
tar -xzf "$BK/workspace.tar.gz"
echo "Restore completed from $BK/workspace.tar.gz"
