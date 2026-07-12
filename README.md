# MSFS 2020 Real-Time Map Tracker

A lightweight, modern, real-time map tracking solution designed specifically for Microsoft Flight Simulator 2020 running on Linux via Proton.

This project uses a network bridge architecture to bypass the limitations of Proton by separating the tracking into two distinct components:
1. **Telemetry Extractor**: A Python script running inside the WINE/Proton prefix alongside MSFS 2020 that extracts flight data via SimConnect and broadcasts it over UDP.
2. **Native Map Application**: A native Linux FastAPI server that listens to the UDP broadcast and serves a beautiful Leaflet.js map in your web browser, updating the aircraft position in real-time via WebSockets.

## Directory Structure

```text
EasyMFSMap/
├── telemetry_extractor/
│   ├── extractor.py        (Runs in Proton, extracts SimConnect data)
│   └── requirements.txt    (Windows Python dependencies)
├── map_server/
│   ├── server.py           (Native Linux FastAPI backend)
│   ├── requirements.txt    (Linux Python dependencies)
│   └── static/
│       └── index.html      (Interactive Leaflet.js frontend)
└── README.md
```

## Prerequisites

1. **Microsoft Flight Simulator 2020** installed via Steam/Proton.
2. **Windows Python** installed inside the MSFS 2020 WINE/Proton prefix.
3. **Native Linux Python** (Python 3.8+) installed on your host system.

## Installation Instructions

### 1. Set up the Native Map Server (Linux Side)

Open a terminal on your Linux host and install the requirements for the map server:

```bash
cd EasyMFSMap/map_server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up the Telemetry Extractor (Proton/WINE Side)

You need to run Windows Python inside the same prefix as MSFS 2020 to access the `SimConnect` API.

1. Download a Windows Python installer (e.g., Python 3.10) and install it using `protontricks` or `WINEPREFIX`.
2. Once installed, run `pip` inside the prefix to install the `SimConnect` library:

```bash
WINEPREFIX="/path/to/SteamLibrary/steamapps/compatdata/1250410/pfx" wine python -m pip install -r telemetry_extractor/requirements.txt
```
*(Ensure you adjust the WINEPREFIX path to your actual MSFS compatdata folder).*

## Execution

To start tracking your flight, follow these steps in order:

### 1. Start the Map Server
On your native Linux terminal:
```bash
cd EasyMFSMap/map_server
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8000
```
Keep this terminal open.

### 2. Open the Map
Open your web browser and navigate to:
```text
http://127.0.0.1:8000
```
You will see the map interface showing "Disconnected" or "Waiting" for data.

### 3. Start Microsoft Flight Simulator 2020
Launch the game normally through Steam and load into a flight.

### 4. Start the Telemetry Extractor
Once loaded into the flight, run the extractor script inside the WINE prefix:

```bash
WINEPREFIX="/path/to/SteamLibrary/steamapps/compatdata/1250410/pfx" wine python EasyMFSMap/telemetry_extractor/extractor.py
```
The script will output `Connected to SimConnect successfully` and begin broadcasting UDP packets to your Linux server. 
The web map will immediately update and show your aircraft's live position.

## Technical Details
- The extractor samples data every 0.5 seconds and sends a small JSON payload over `UDP 127.0.0.1:5000`.
- The native FastAPI server listens on `UDP 5000` and relays the telemetry payload to the connected browser client over WebSockets.
- All code is strictly documented and written in English.
