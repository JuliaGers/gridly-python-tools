import urllib.request
import urllib.parse
import json
import sys
import os

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        raise FileNotFoundError("No .env file found. Place it in the same folder as this script.")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()

load_env()
API_KEY = os.environ.get("API_KEY")
VIEW_ID = os.environ.get("VIEW_ID")

# Fetch all records once at startup
print("\nLoading database...")
all_records = []
offset = 0
limit = 1000
while True:
    params = urllib.parse.urlencode({"page": json.dumps({"offset": offset, "limit": limit})})
    url = f"https://api.gridly.com/v1/views/{VIEW_ID}/records?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"ApiKey {API_KEY}"})
    with urllib.request.urlopen(req) as res:
        records = json.loads(res.read())
    all_records.extend(records)
    if len(records) < limit:
        break
    offset += limit

print(f"Ready - {len(all_records):,} records loaded.\n")

# Search loop
while True:
    query = input("Search for (or press Enter to quit): ").strip().lower()
    if not query:
        print("Goodbye!")
        break

    hits = []
    for record in all_records:
        matched_columns = []
        # Search the Record ID itself
        if query in str(record["id"]).lower():
            matched_columns.extend(
                (cell["columnId"], cell.get("value", ""))
                for cell in record.get("cells", [])
                if isinstance(cell.get("value"), str)
            )
        # Search all cell values
        for cell in record.get("cells", []):
            value = cell.get("value")
            if isinstance(value, str) and query in value.lower():
                matched_columns.append((cell["columnId"], value))
        if matched_columns:
            hits.append((record["id"], matched_columns))

    print()
    if not hits:
        print("No matches found.\n")
    else:
        print(f"Found {len(hits)} matching record(s):\n")
        print(f"{'ID':<10} {'COLUMN':<20} VALUE")
        print("-" * 80)
        for record_id, columns in hits:
            for i, (col_id, value) in enumerate(columns):
                id_display = record_id if i == 0 else ""
                display_val = value if len(value) <= 60 else value[:57] + "..."
                print(f"{id_display:<10} {col_id:<20} {display_val}")
            if len(columns) > 1:
                print()
        print(f"\n{len(hits)} result(s) for \"{query}\"\n")