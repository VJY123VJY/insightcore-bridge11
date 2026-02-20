import subprocess
import time
import os
import signal
import sys
from datetime import datetime

processes = []
os.makedirs("logs", exist_ok=True)


def now():
    """Return formatted current time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def start_service(name, script_path, port):
    print(f"[{now()}] Starting {name} on port {port}...")

    log_path = f"logs/{name.lower().replace(' ', '_')}.log"
    log_file = open(log_path, "w")

    # Write startup header in log file
    log_file.write(f"[{now()}] {name} service starting on port {port}\n")
    log_file.flush()

    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    cmd = [sys.executable, script_path]

    p = subprocess.Popen(
        cmd,
        env=env,
        stdout=log_file,
        stderr=subprocess.STDOUT
    )

    processes.append((p, log_file))

    time.sleep(1)  # Reduced startup delay


def cleanup():
    print(f"\n[{now()}] Shutting down services...")

    for p, log in processes:
        p.terminate()
        log.write(f"\n[{now()}] Service terminated.\n")
        log.close()

    print(f"[{now()}] All services stopped.")


def main():
    try:
        print(f"[{now()}] Sovereign Stack Boot Sequence Initiated\n")

        # Start Core
        start_service("Core", "core/issuer.py", 5503)

        # Start Flow
        start_service("Flow", "flow/ingestor.py", 5502)

        # Start Bridge
        start_service("Bridge", "bridge/enforcer.py", 5500)

        print(f"\n[{now()}] All systems active.")
        print(f"[{now()}] Logs available in /logs/")
        print(f"[{now()}] Run verification/day1_validation.py to test.\n")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        cleanup()

    except Exception as e:
        print(f"[{now()}] ERROR: {e}")
        cleanup()


if __name__ == "__main__":
    main()