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

def find_msfs_prefix():
    print("\n=== Locating MSFS 2020 Steam Prefix ===")
    common_paths = [
        os.path.expanduser(f"~/.steam/steam/steamapps/compatdata/{MSFS_APPID}/pfx"),
        os.path.expanduser(f"~/.local/share/Steam/steamapps/compatdata/{MSFS_APPID}/pfx")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"Found prefix at: {path}")
            return path
            
    print("Could not automatically locate the MSFS 2020 WINE prefix.")
    print(f"Example: /home/user/.steam/steam/steamapps/compatdata/{MSFS_APPID}/pfx")
    custom_path = input(f"Please enter the path to the MSFS compatdata/{MSFS_APPID}/pfx folder: ").strip()
    if not os.path.exists(custom_path) or not os.path.exists(os.path.join(custom_path, "drive_c")):
        print("\nError: The specified path does not exist or is not a valid WINE prefix (missing 'drive_c' folder). Exiting.")
        sys.exit(1)
    return custom_path

def ensure_windows_python(wine_prefix):
    print("\n=== Verifying Windows Python in WINE Prefix ===")
    env = os.environ.copy()
    env["WINEPREFIX"] = wine_prefix
    
    print("Checking if Windows Python is installed...")
    result = subprocess.run(["wine", "python", "--version"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if result.returncode != 0:
        print("Windows Python not found in WINE prefix. Downloading installer...")
        if not os.path.exists(PYTHON_INSTALLER_FILE):
            print(f"Downloading {PYTHON_INSTALLER_FILE}...")
            urllib.request.urlretrieve(PYTHON_INSTALLER_URL, PYTHON_INSTALLER_FILE)
            print("Download complete.")
            
        print("Installing Windows Python silently via WINE. This may take a moment...")
        run_cmd(["wine", PYTHON_INSTALLER_FILE, "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0"], env=env)
        print("Windows Python installed successfully.")
    else:
        print("Windows Python is already installed.")

def install_windows_dependencies(wine_prefix):
    print("\n=== Installing Windows Dependencies (SimConnect) ===")
    env = os.environ.copy()
    env["WINEPREFIX"] = wine_prefix
    run_cmd(["wine", "python", "-m", "pip", "install", "SimConnect==0.4.38"], env=env)

def start_server_and_browser(venv_dir):
    print("\n=== Starting Map Server ===")
    uvicorn_exe = os.path.join(venv_dir, "bin", "uvicorn")
    server_process = subprocess.Popen([uvicorn_exe, "map_server.server:app", "--host", "0.0.0.0", "--port", "8000"])
    
    print("Opening browser in 2 seconds...")
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")
    
    return server_process

def start_extractor(wine_prefix):
    print("\n=== Telemetry Extractor ===")
    input("Press Enter when your flight is loaded and ready in MSFS 2020...")
    
    env = os.environ.copy()
    env["WINEPREFIX"] = wine_prefix
    extractor_path = os.path.join("telemetry_extractor", "extractor.py")
    
    print("Starting Telemetry Extractor inside WINE...")
    extractor_process = subprocess.Popen(["wine", "python", extractor_path], env=env)
    return extractor_process

def check_wine():
    if shutil.which("wine") is None:
        print("\n'wine' is not installed or not found in your system PATH.")
        print("Attempting to install WINE automatically. You may be prompted for your sudo password.")
        
        if shutil.which("apt"):
            run_cmd(["sudo", "apt", "update"])
            run_cmd(["sudo", "apt", "install", "-y", "wine"])
        elif shutil.which("dnf"):
            run_cmd(["sudo", "rpm-ostree", "install", "-y", "wine"]) # Fedora Atomic images utilize rpm-ostree instead of dnf
        elif shutil.which("pacman"):
            run_cmd(["sudo", "pacman", "-S", "--noconfirm", "wine"])
        elif shutil.which("zypper"):
            run_cmd(["sudo", "zypper", "install", "-y", "wine"])
        else:
            print("Could not determine your package manager. Please install WINE manually.")
            sys.exit(1)
            
        if shutil.which("wine") is None:
            print("WINE installation failed or executable still not found. Please install it manually.")
            sys.exit(1)
        print("WINE installed successfully.")

def main():
    print("========================================")
    print("    EasyMFSMap Automated Executer       ")
    print("========================================")
    
    check_wine()
    
    venv_dir = setup_linux_venv()
    wine_prefix = find_msfs_prefix()
    
    ensure_windows_python(wine_prefix)
    install_windows_dependencies(wine_prefix)
    
    server_process = start_server_and_browser(venv_dir)
    
    try:
        extractor_process = start_extractor(wine_prefix)
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
