# Elite Exobiologist Route Sorter (EERS)

A minimalist Python utility using a Greedy Pathfinding Algorithm to calculate the shortest distance-based route through a custom list of Elite Dangerous star systems. Designed for efficient Exobiology data collection.

## Project Files

| File | Purpose |
| :--- | :--- |
| `eers.py` | The core Python script containing the route calculation logic. |
| `target_data_input.txt` | **REQUIRED INPUT.** Edit this file to add your `System Name | Body String` pairs. |
| `run_eers.bat` | **Windows Launcher.** Double-click this to run the script without using the `cd` command. |


## TL;DR

1.  **Install Requests** (One-time setup): Open your terminal/PowerShell and run:
    ```bash
    py -m pip install requests
    ```
2.  **Edit Input:** Open and edit `target_data_input.txt` with your desired systems.
3.  **Run:** Double-click `run_eers.bat`.
4.  **Enter Start System:** Type your starting system (e.g., `Kwatee`) when prompted.


## Full Setup and Usage

### 1. Prerequisites

* **Python 3.x:** Must be installed and accessible using the `py` command.
* **The `requests` library:** Required for fetching system coordinates from the EDSM API.

### 2. Installation (Dependencies)

If you haven't run the Quick Start command, open your terminal (PowerShell, Command Prompt, or similar) and execute:

```bash
py -m pip install requests
