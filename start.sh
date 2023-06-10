#!/bin/bash



# Create file consisting of PID process
source Venv/bin/activate
python3 main.py &> temp_outut.txt &
pid=$(pgrep -f "python3 main.py")
touch "${pid}"

