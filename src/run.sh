#!/bin/bash
set -Eeuo pipefail

python -u ./src/main.py --data=/data | cat

# Catch segmentation fault in Python (TDE library)
if [[ PIPESTATUS[0] -eq 139 ]]; then
  echo "TDE export failed (segmentation fault).";
  echo "Please check that your data matches the configured data types and formats."
  echo "For example, if you try to export \"0020-02-18\" as the date, the export will fail."
  exit 1
fi
