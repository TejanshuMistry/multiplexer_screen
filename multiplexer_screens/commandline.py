import subprocess
import re
import time

def get_ngrok_tcp_details(port):
    try:
        # Start ngrok TCP as a subprocess
        process = subprocess.Popen(
            ["ngrok", "tcp", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give ngrok time to initialize and start printing the output
        time.sleep(5)  # Adjust sleep time if needed

        # Parse the output line by line
        for line in process.stdout:
            print(line.strip())  # Optional: Print live output for debugging

            # Look for the public TCP address pattern
            match = re.search(r"tcp://([\d.]+):(\d+)", line)
            if match:
                public_address = match.group(1)
                public_port = match.group(2)
                print(f"Public Address: {public_address}")
                print(f"Public Port: {public_port}")
                process.terminate()  # Terminate the ngrok process if needed
                return public_address, public_port

        # Check if ngrok failed to output the expected info
        print("No TCP details found in ngrok output.")

    except Exception as e:
        print(f"Error: {e}")

# Example: Run ngrok and extract TCP details for local port 8765
tcp_details = get_ngrok_tcp_details(8765)
if tcp_details:
    print(f"Extracted TCP Details: Address={tcp_details[0]}, Port={tcp_details[1]}")