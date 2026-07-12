import os
import sys
import subprocess
import urllib.request
import webbrowser
import time
import shutil

PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
PYTHON_INSTALLER_FILE = "python-3.10.11-amd64.exe"
MSFS_APPID = "1250410"

def run_cmd(cmd, env=None, check=True, shell=False):
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, env=env, shell=shell)
    if check and result.returncode != 0:
        print(f"Error executing command. Return code: {result.returncode}")
        sys.exit(result.returncode)
    return result.returncode

def setup_linux_venv():
    print("\n=== Setting up Native Linux Environment ===")
    venv_dir = os.path.join(os.getcwd(), "venv")
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        run_cmd([sys.executable, "-m", "venv", "venv"])
    
    pip_exe = os.path.join(venv_dir, "bin", "pip")
    print("Installing requirements...")
    run_cmd([pip_exe, "install", "fastapi", "uvicorn", "websockets"])
    return venv_dir



def ensure_windows_python():
    print("\n=== Verifying Windows Python in Proton Prefix ===")
    
    print("Checking if Windows Python is installed...")
    result = subprocess.run(["protontricks", "-c", "wine python --version", MSFS_APPID], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if result.returncode != 0:
        print("Windows Python not found in Proton prefix. Downloading installer...")
        if not os.path.exists(PYTHON_INSTALLER_FILE):
            print(f"Downloading {PYTHON_INSTALLER_FILE}...")
            urllib.request.urlretrieve(PYTHON_INSTALLER_URL, PYTHON_INSTALLER_FILE)
            print("Download complete.")
            
        print("Installing Windows Python silently via Protontricks. This may take a moment...")
        abs_installer = os.path.abspath(PYTHON_INSTALLER_FILE)
        cmd_str = f"wine {abs_installer} /quiet InstallAllUsers=0 PrependPath=1 Include_test=0"
        run_cmd(["protontricks", "-c", cmd_str, MSFS_APPID])
        print("Windows Python installed successfully.")
    else:
        print("Windows Python is already installed.")

def install_windows_dependencies():
    print("\n=== Installing Windows Dependencies (SimConnect) ===")
    run_cmd(["protontricks", "-c", "wine python -m pip install SimConnect", MSFS_APPID])

def start_server_and_browser(venv_dir):
    print("\n=== Starting Map Server ===")
    uvicorn_exe = os.path.join(venv_dir, "bin", "uvicorn")
    server_process = subprocess.Popen([uvicorn_exe, "map_server.server:app", "--host", "0.0.0.0", "--port", "8000"])
    
    print("Opening browser in 2 seconds...")
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")
    
    return server_process

def start_extractor():
    print("\n=== Telemetry Extractor ===")
    input("Press Enter when your flight is loaded and ready in MSFS 2020...")
    
    extractor_path = os.path.abspath(os.path.join("telemetry_extractor", "extractor.py"))
    
    print("Starting Telemetry Extractor inside Proton...")
    extractor_process = subprocess.Popen(["protontricks", "-c", f"wine python '{extractor_path}'", MSFS_APPID])
    return extractor_process

def check_protontricks():
    if shutil.which("protontricks") is None:
        print("\n'protontricks' is not installed or not found in your system PATH.")
        print("We use protontricks to safely interface with the MSFS Proton environment.")
        print("Please install protontricks (e.g., via your package manager or flatpak) and run this script again.")
        sys.exit(1)

def main():
    print("========================================")
    print("    EasyMFSMap Automated Executer       ")
    print("========================================")
    
    check_protontricks()
    
    venv_dir = setup_linux_venv()
    
    ensure_windows_python()
    install_windows_dependencies()
    
    server_process = start_server_and_browser(venv_dir)
    
    try:
        extractor_process = start_extractor()
        print("\nAll processes running. Press Ctrl+C to exit.")
        extractor_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server_process.terminate()
        try:
            extractor_process.terminate()
        except Exception:
            pass
        print("Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()
