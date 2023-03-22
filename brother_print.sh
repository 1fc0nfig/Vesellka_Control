#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <path_to_directory>"
  exit 1
fi

DIRECTORY=$1

for FILE in $DIRECTORY/*.png; do
  if [ -f "$FILE" ]; then
    echo "Printing $FILE"
    brother_ql -p usb://0x04f9:0x2042 -m QL-700 print -l 62 "$FILE"
  fi
done
