#!/bin/bash

echo "Running Python scripts in separate terminals..."

# Function to run a Python script in a new terminal
run_script() {
    gnome-terminal -- bash -c "export PYTHONIOENCODING=utf-8; export LANG=ko_KR.UTF-8; python3 $1; exec bash"
}

# Run each script in a new terminal
run_script "./Intelligence_Vehicle_Service/ServiceMain.py"
run_script "./Intelligence_Vehicle_GUI/GUIMain.py"
run_script "./Intelligence_Vehicle_AI/Perception/Lane/LaneMain.py"
run_script "./Intelligence_Vehicle_AI/Perception/Object/ObstacleMain.py"
echo "All scripts launched. Check individual terminals for output."

# source launch_scripts.sh 
# 또는 
# . launch_scripts.sh