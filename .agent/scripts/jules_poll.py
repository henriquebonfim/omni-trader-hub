import subprocess
import time
import sys
import argparse
import re

def get_session_status(session_id):
    try:
        # Use COLUMNS=200 to ensure the output isn't truncated
        result = subprocess.run(
            ["jules", "remote", "list", "--session"],
            capture_output=True,
            text=True,
            env={"COLUMNS": "200"}
        )
        if result.returncode != 0:
            print(f"Error running jules command: {result.stderr}", file=sys.stderr)
            return None

        lines = result.stdout.strip().split('
')
        for line in lines:
            if session_id in line:
                # Basic parsing: ID is usually the first column, Status is the last
                parts = line.split()
                if len(parts) >= 2:
                    # Status is likely the last part
                    status = parts[-1]
                    return status
        
        return "NOT_FOUND"
    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Poll Jules session status")
    parser.add_argument("--id", required=True, help="Session ID to poll")
    parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds")
    
    args = parser.parse_args()
    
    start_time = time.time()
    print(f"Polling status for session {args.id}...")
    
    while True:
        status = get_session_status(args.id)
        
        if status == "COMPLETED" or status == "DONE" or status == "FINISHED":
            print(f"Session {args.id} completed successfully.")
            sys.exit(0)
        elif status == "FAILED" or status == "ERROR":
            print(f"Session {args.id} failed.")
            sys.exit(1)
        elif status == "NOT_FOUND":
            # If it's not found, it might have completed and been removed from the list
            # We should probably check if there's any other indicator, but for now
            # let's assume not found means it's no longer active.
            print(f"Session {args.id} no longer found in active list. Assuming completion.")
            sys.exit(0)
        
        print(f"Session {args.id} status: {status}. Waiting {args.interval}s...")
        
        if time.time() - start_time > args.timeout:
            print(f"Timeout reached after {args.timeout} seconds.")
            sys.exit(1)
            
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
