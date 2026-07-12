import json
import socket
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="MSFS Map Tracker Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UDP_IP = "127.0.0.1"
UDP_PORT = 5000

telemetry_data = {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "heading": 0.0
}

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

def udp_listener():
    global telemetry_data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening for UDP telemetry on {UDP_IP}:{UDP_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            payload = data.decode('utf-8')
            telemetry_data = json.loads(payload)
        except Exception as e:
            print(f"Error in UDP listener: {e}")

@app.on_event("startup")
async def startup_event():
    listener_thread = threading.Thread(target=udp_listener, daemon=True)
    listener_thread.start()

@app.get("/")
async def get_index():
    index_path = os.path.join(static_dir, "index.html")
    with open(index_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via WebSocket.")
    try:
        while True:
            await websocket.send_json(telemetry_data)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        print("Client disconnected.")
