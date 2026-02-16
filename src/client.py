import sys
import requests

# Reviewer: Server URL for API endpoints
SERVER_URL = "http://127.0.0.1:8000"

# Reviewer: Uploads a text file to the server using the load() API.
def load(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{SERVER_URL}/load/", files=files)
        print(resp.json())

# Reviewer: Requests N random lines from the server using the sample() API.
def sample(n):
    resp = requests.post(f"{SERVER_URL}/sample/", params={"n": n})
    data = resp.json()
    if "sampled_lines" in data:
        for i, line in enumerate(data["sampled_lines"], 1):
            print(f"{i}: {line}")
    else:
        print(data)

# Reviewer: Entry point for command-line usage.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: client.py load <file_path> | sample <N>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "load" and len(sys.argv) == 3:
        load(sys.argv[2])
    elif cmd == "sample" and len(sys.argv) == 3:
        sample(int(sys.argv[2]))
    else:
        print("Usage: client.py load <file_path> | sample <N>")
