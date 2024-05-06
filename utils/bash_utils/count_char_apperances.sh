#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <directory_path> <symbol>"
    exit 1
fi

directory="$1"
symbol="$2"

escaped_symbol=$(printf '%s\n' "$symbol" | sed -e 's/[]\/$*.^[]/\\&/g')

count=0

for file in "$directory"/*
do
    if [ -f "$file" ]; then
        occurrences=$(grep -o "$escaped_symbol" "$file" | wc -l)
        count=$((count + occurrences))
        echo $count
    fi
done

# Print the total count
echo "Total number of '$symbol' occurrences in files: $count"