import urllib.request
import urllib.parse
import json
import os

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env file not found at {env_path}\nPlease place a .env file in the same folder as this script.")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()

load_env()
API_KEY = os.environ.get("API_KEY")
VIEW_ID = os.environ.get("VIEW_ID")

if not API_KEY or not VIEW_ID:
    raise ValueError("API_KEY and VIEW_ID must both be set in your .env file.")

all_ids = []
offset = 0
limit = 1000

print("Fetching records...")

while True:
    params = urllib.parse.urlencode({"page": json.dumps({"offset": offset, "limit": limit})})
    url = f"https://api.gridly.com/v1/views/{VIEW_ID}/records?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"ApiKey {API_KEY}"})
    with urllib.request.urlopen(req) as res:
        records = json.loads(res.read())
    ids = [int(r["id"]) for r in records if r["id"].isdigit()]
    all_ids.extend(ids)
    print(f"  Fetched {offset + len(records)} records so far...")
    if len(records) < limit:
        break
    offset += limit

highest = max(all_ids)
next_id = highest + 1

import subprocess
import platform
if platform.system() == "Darwin":
    subprocess.run("pbcopy", input=str(next_id).encode(), check=True)
elif platform.system() == "Windows":
    subprocess.run("clip", input=str(next_id).encode(), check=True)

print(f"\nTotal records: {len(all_ids)}")
print(f"Highest existing ID: {highest}")
print(f"\n>>> Next free Record ID: {next_id} <<< (copied to clipboard!)")

input("\nPress Enter to close...")
