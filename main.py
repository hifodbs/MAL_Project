import subprocess
import sys
import time
import socket
from pathlib import Path

def is_backend_ready(host="127.0.0.1", port=5000):
    """Checks if Flask is listening on port 5000."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex((host, port)) == 0

def run_app():
    project_root = Path(__file__).parent.resolve()
    frontend_dir = project_root / "frontend"

    backend_cmd = [sys.executable, "-m", "backend.app"]
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]

    print(f"--- Launching MAL Project from {project_root} ---")

    try:
        print("1. Starting Flask Backend...")
        backend_process = subprocess.Popen(backend_cmd, cwd=project_root)

        print(" Waiting for Flask to initialize on port 5000...")
        
        server_ready = False
        for i in range(30): 
            if is_backend_ready(port=5000):
                print("SUCCESS: Flask is online!")
                server_ready = True
                break
            time.sleep(1)
            
        if not server_ready:
            print(f"\nERROR: Flask failed to start within 30 seconds.")
            print("Exiting pipeline to prevent errors.")
            backend_process.terminate()
            sys.exit(1)

        print("2. Starting Streamlit Frontend...")
        frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

        print("\nSYSTEM RUNNING. Press Ctrl+C to stop.")

        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\nStopping services...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    run_app()