#!/bin/bash

# Ensure conda is initialized
eval "$(conda shell.bash hook)"

ENV_NAME="dash_env"
REQ_FILE="requirements.txt"
APP1_DIR="DashboardV1"
APP2_DIR="DashboardV2"
APP1_SCRIPT="app.py"
APP2_SCRIPT="app.py"
SESSION1="dash_app1"
SESSION2="dash_app2"

# Function to create conda env if not exists
create_conda_env() {
    if conda info --envs | grep -q "$ENV_NAME"; then
        echo "Conda environment '$ENV_NAME' already exists."
    else
        echo "Creating conda environment '$ENV_NAME'..."
        conda create -y -n "$ENV_NAME" python=3.10
    fi
}

# Function to install requirements
install_requirements() {
    echo "Installing dependencies (if not already installed)..."
    conda activate "$ENV_NAME"
    pip install --upgrade pip
    pip install -r "$REQ_FILE"
}

# Function to start Dash apps
start_apps() {
    echo "Starting Dash apps in tmux sessions..."

    tmux new-session -d -s $SESSION1 "bash -c 'eval \"\$(conda shell.bash hook)\" && conda activate $ENV_NAME && cd $APP1_DIR && python3 $APP1_SCRIPT'"
    tmux new-session -d -s $SESSION2 "bash -c 'eval \"\$(conda shell.bash hook)\" && conda activate $ENV_NAME && cd $APP2_DIR && python3 $APP2_SCRIPT'"


    echo " Dash apps are running in tmux sessions: $SESSION1 and $SESSION2"
    echo " Full Comparision App 1: http://localhost:8050"
    echo " Cost Comparision App 2: http://localhost:8040"
    echo " Use 'tmux attach -t $SESSION1' to view app1, and 'tmux attach -t $SESSION2' for app2."
}

# Function to kill sessions
stop_apps() {
    echo "Stopping Dash apps..."
    tmux kill-session -t $SESSION1 2>/dev/null
    tmux kill-session -t $SESSION2 2>/dev/null
    echo "All tmux sessions stopped."
}

# User menu
echo "Choose an option:"
select opt in "Start Apps" "Stop Apps" "Restart Apps" "Exit"; do
    case $opt in
        "Start Apps")
            create_conda_env
            conda activate "$ENV_NAME"
            install_requirements
            start_apps
            break
            ;;
        "Stop Apps")
            stop_apps
            break
            ;;
        "Restart Apps")
            stop_apps
            create_conda_env
            conda activate "$ENV_NAME"
            install_requirements
            start_apps
            break
            ;;
        "Exit")
            echo "Exiting..."
            break
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
done
