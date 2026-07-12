# MSFS 2020 Real-Time Map Tracker

A lightweight, modern, real-time map tracking solution designed specifically for Microsoft Flight Simulator 2020 running on Linux via Proton.

This project uses a network bridge architecture to bypass the limitations of Proton by separating the tracking into two distinct components:
1. **Telemetry Extractor**: A Python script running inside the WINE/Proton prefix alongside MSFS 2020 that extracts flight data via SimConnect and broadcasts it over UDP.
2. **Native Map Application**: A native Linux FastAPI server that listens to the UDP broadcast and serves a beautiful Leaflet.js map in your web browser, updating the aircraft position in real-time via WebSockets.

## Directory Structure

```text
EasyMFSMap/
├── main.py                 (Automated setup and execution orchestrator)
├── requirements.txt        (Combined dependencies)
├── telemetry_extractor/
│   └── extractor.py        (Runs in Proton, extracts SimConnect data)
└── map_server/
    ├── server.py           (Native Linux FastAPI backend)
    └── static/
        └── index.html      (Interactive Leaflet.js frontend)
```

## Prerequisites

1. **Microsoft Flight Simulator 2020** installed via Steam/Proton.
2. **Native Linux Python** (Python 3.8+) installed on your host system.
3. **WINE** installed on your system.

## Quick Start (Automated Setup)

The easiest way to run the tracker is to use the included `main.py` script. It will automatically create virtual environments, install dependencies, find your MSFS 2020 installation, and install Windows Python inside the prefix if necessary.

Open a terminal in the root directory of this project and run:

```bash
python3 main.py
```

### What `main.py` does:
1. Sets up a local Linux `venv` and installs the required server packages (`fastapi`, `uvicorn`, `websockets`).
2. Automatically locates your MSFS 2020 Steam prefix (`compatdata/1250410/pfx`).
3. Checks if Windows Python is installed in that prefix. If not, it downloads and silently installs Python 3.10 via WINE.
4. Installs the `SimConnect` library into the WINE prefix.
5. Starts the map server natively and opens your default web browser.
6. Prompts you to press Enter once your flight is loaded in the game, and then starts the telemetry extractor inside WINE.

## Manual Execution (Advanced)

If you prefer to start things manually:

### 1. Start the Map Server
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn map_server.server:app --host 0.0.0.0 --port 8000
```

### 2. Start the Telemetry Extractor
Ensure you have Windows Python and `SimConnect` installed in your WINE prefix, then run:
```bash
WINEPREFIX="/path/to/SteamLibrary/steamapps/compatdata/1250410/pfx" wine python telemetry_extractor/extractor.py
```

## Technical Details
- The extractor samples data every 0.5 seconds and sends a small JSON payload over `UDP 127.0.0.1:5000`.
- The native FastAPI server listens on `UDP 5000` and relays the telemetry payload to the connected browser client over WebSockets.
- All code is strictly documented and written in English.
