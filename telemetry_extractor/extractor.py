import socket
import json
import time
from SimConnect import SimConnect, AircraftRequests

# Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
UPDATE_INTERVAL = 0.5  # seconds

def main():
    print("Starting MSFS Telemetry Extractor...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sm = None
    aq = None

    while True:
        try:
            if sm is None:
                print("Attempting to connect to SimConnect...")
                # The SimConnect library requires a running MSFS instance
                sm = SimConnect()
                aq = AircraftRequests(sm, _time=0)
                print("Connected to SimConnect successfully.")

            lat = aq.get("PLANE_LATITUDE")
            lon = aq.get("PLANE_LONGITUDE")
            alt = aq.get("PLANE_ALTITUDE")
            heading = aq.get("PLANE_HEADING_DEGREES_TRUE")

            if lat is not None and lon is not None:
                data = {
                    "latitude": float(lat),
                    "longitude": float(lon),
                    "altitude": float(alt),
                    "heading": float(heading)
                }
                
                payload = json.dumps(data).encode('utf-8')
                sock.sendto(payload, (UDP_IP, UDP_PORT))
                print(f"Sent: {data}")
            else:
                print("Waiting for valid aircraft data...")

        except Exception as e:
            print(f"Connection lost or error: {e}. Retrying in 5 seconds...")
            sm = None
            time.sleep(5)
            continue

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
