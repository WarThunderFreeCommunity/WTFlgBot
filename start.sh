#!/bin/bash

digit_files=$(find . -maxdepth 1 -type f -name '[0-9]*')

for file in $digit_files; do
    pid=$(basename "$file")
    kill $pid
done

rm $digit_files

# Create file consisting of PID process
source Venv/bin/activate
python3 main.py &> temp_outut.txt &
pid=$(pgrep -f "python3 main.py")
touch "${pid}"
