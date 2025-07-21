#!/bin/bash

{
for file in /storage2/bitcoin/blocks/blk*.dat; do
  echo "#################"
  date +"%Y-%m-%d - %H:%M:%S"
  echo "DAT File: ${file}"
  echo "Messages:"
  strings -20 "$file"
done
} > messages_all.log
