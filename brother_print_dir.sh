#!/bin/bash

read -p "Enter path to directory: " DIRECTORY

if [ ! -d "$DIRECTORY" ]; then
  echo "Error: '$DIRECTORY' is not a valid directory."
  exit 1
fi

for FILE in "$DIRECTORY"/*.png; do
  if [ -f "$FILE" ]; then
    echo "Printing $FILE"
    brother_ql -p usb://0x04f9:0x2042 -m QL-700 print -l 62 "$FILE"
  fi
done
