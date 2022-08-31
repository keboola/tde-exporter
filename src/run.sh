#!/bin/bash

python -u ./src/main.py --data=/data | cat

MAIN_PY_EXIT_CODE=PIPESTATUS[0]

# Catch segmentation fault in Python (TDE library)
if [[ $MAIN_PY_EXIT_CODE -eq 139 ]]; then
  echo "TDE export failed (segmentation fault).";
  echo "Please check that your data matches the configured data types and formats."
  echo "For example, if you try to export \"0020-02-18\" as the date, the export will fail."
  exit 1
fi

exit $MAIN_PY_EXIT_CODE
