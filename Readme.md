# Dash Application Launcher with Conda and Tmux

This repository provides a Bash script to automate the setup and launch of two separate Dash applications using:

* Conda (for virtual environment and dependencies)
* Tmux (to run apps in parallel terminal sessions)
* Dash (interactive web apps)

---

## Project Structure

```
├── DashboardV1/
│   └── app.py          # First Dash App (Full Comparison)
├── DashboardV2/
│   └── app.py          # Second Dash App (Cost Comparison)
├── requirements.txt    # Python dependencies for both apps
└── run_dash.sh         # Main launcher script
```

---

## Prerequisites

* Miniconda or Anaconda
* tmux

Install tmux if missing:

```bash
sudo apt update
sudo apt install tmux
```

---

## Usage Instructions

Make sure the script is executable:

```bash
chmod +x run_dash.sh
```

Then run the script:

```bash
./run_dash.sh
```

You will be prompted with:

```
Choose an option:
1) Start Apps
2) Stop Apps
3) Restart Apps
4) Exit
```

---

## What Each Option Does

**Start Apps**

* Creates a Conda environment `dash_env` (if not already existing)
* Installs dependencies from `requirements.txt`
* Launches:

  * DashboardV1 on port 8050 in tmux session `dash_app1`
  * DashboardV2 on port 8040 in tmux session `dash_app2`

**Stop Apps**

* Kills both tmux sessions (`dash_app1` and `dash_app2`)

**Restart Apps**

* Stops and then reinitializes everything from scratch

---

## Accessing the Apps

* App 1 (Full Comparison): [http://localhost:8050](http://localhost:8050)
* App 2 (Cost Comparison): [http://localhost:8040](http://localhost:8040)

---

## Managing tmux Sessions

Attach to a running session:

```bash
tmux attach -t dash_app1   # View App 1
tmux attach -t dash_app2   # View App 2
```

Detach from tmux by pressing:

```
Ctrl + B, then D
```

---

## Notes

* Make sure both apps use different ports (already set to 8050 and 8040)
* Adjust paths or environment names in `run_dash.sh` if needed

