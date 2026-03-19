"""
Create_Gridly_String.py
=======================
A local web tool for creating new string records in a Gridly view.

How it works:
  - Reads API_KEY and VIEW_ID from a .env file in the same folder as this script.
  - Spins up a lightweight local HTTP server and opens a browser UI automatically.
  - The UI fetches all existing records to determine the next available numeric Record ID.
  - You fill in an English string (required), an optional German translation, an optional
    Description, and an optional Comment, then click "Create Record".
  - The record is posted directly to the Gridly API and the ID counter refreshes.

Setup:
  1. Create a .env file next to this script with:
       API_KEY=<your Gridly API key>
       VIEW_ID=<your Gridly view ID>
  2. Run:  python Create_Gridly_String.py
  3. A browser tab will open automatically. Press Ctrl+C in the terminal to stop.

Column mapping:
  - ENG          → English source string (required)
  - OurRecordID  → Auto-assigned numeric ID
  - GER          → German translation / Target_deDE (optional)
  - Description  → Context or usage notes (optional)
  - Comment      → Internal comments (optional)
"""

import urllib.request
import urllib.parse
import json
import threading
import webbrowser
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        msg = ".env file not found at " + env_path + "\nPlease place a .env file in the same folder as this script."
        raise FileNotFoundError(msg)
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()

load_env()
API_KEY = os.environ.get("API_KEY")
VIEW_ID  = os.environ.get("VIEW_ID")

if not API_KEY or not VIEW_ID:
    raise ValueError("API_KEY and VIEW_ID must both be set in your .env file.")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Gridly Record ID Tool</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f7; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 2rem; }
  .card { background: white; border-radius: 16px; padding: 2.5rem; width: 100%; max-width: 480px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
  h1 { font-size: 1.4rem; font-weight: 600; color: #1d1d1f; margin-bottom: 0.25rem; }
  .subtitle { font-size: 0.85rem; color: #888; margin-bottom: 2rem; }
  .next-id-box { background: #f5f5f7; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 2rem; }
  .next-id-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #888; margin-bottom: 0.5rem; }
  .next-id-value { font-size: 3rem; font-weight: 700; color: #1d1d1f; font-variant-numeric: tabular-nums; }
  .next-id-value.loading { color: #ccc; font-size: 1.5rem; font-weight: 400; }
  .meta { font-size: 0.75rem; color: #aaa; margin-top: 0.5rem; }
  .divider { border: none; border-top: 1px solid #f0f0f0; margin: 0 0 1.5rem; }
  label { display: block; font-size: 0.8rem; font-weight: 500; color: #555; margin-bottom: 0.4rem; }
  input[type="text"] { width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 0.65rem 0.9rem; font-size: 0.95rem; outline: none; transition: border 0.2s; }
  input[type="text"]:focus { border-color: #0071e3; }
  .field-group { margin-bottom: 1rem; }
  .required { color: #ff3b30; }
  .optional { color: #aaa; font-weight: 400; }
  .btn { width: 100%; background: #0071e3; color: white; border: none; border-radius: 8px; padding: 0.75rem; font-size: 0.95rem; font-weight: 500; cursor: pointer; margin-top: 0.75rem; transition: background 0.2s; }
  .btn:hover { background: #0077ed; }
  .btn:disabled { background: #ccc; cursor: not-allowed; }
  .btn-secondary { background: #f5f5f7; color: #1d1d1f; margin-top: 0.5rem; }
  .btn-secondary:hover { background: #e8e8ed; }
  .status { margin-top: 1rem; font-size: 0.85rem; text-align: center; min-height: 1.2em; }
  .status.success { color: #34c759; }
  .status.error { color: #ff3b30; }
</style>
</head>
<body>
<div class="card">
  <h1>Gridly Record ID Tool</h1>
  <p class="subtitle">View: __VIEW_ID__</p>

  <div class="next-id-box">
    <div class="next-id-label">Next Free Record ID</div>
    <div class="next-id-value loading" id="nextId">Loading…</div>
    <div class="meta" id="meta"></div>
  </div>

  <hr class="divider"/>

  <div class="field-group">
    <label for="engValue">English string <span class="required">*</span></label>
    <input type="text" id="engValue" placeholder="Required…" />
  </div>
  <div class="field-group">
    <label for="deValue">German translation — Target_deDE <span class="optional">(optional)</span></label>
    <input type="text" id="deValue" placeholder="Optional…" />
  </div>
  <div class="field-group">
    <label for="descValue">Description <span class="optional">(optional)</span></label>
    <input type="text" id="descValue" placeholder="Optional…" />
  </div>
  <div class="field-group">
    <label for="commentValue">Comment <span class="optional">(optional)</span></label>
    <input type="text" id="commentValue" placeholder="Optional…" />
  </div>

  <button class="btn" id="createBtn" onclick="createRecord()" disabled>Create Record</button>
  <button class="btn btn-secondary" onclick="refresh()">↻ Refresh ID</button>

  <div class="status" id="status"></div>
</div>

<script>
  let nextId = null;

  async function refresh() {
    document.getElementById('nextId').className = 'next-id-value loading';
    document.getElementById('nextId').textContent = 'Loading…';
    document.getElementById('meta').textContent = '';
    document.getElementById('createBtn').disabled = true;
    document.getElementById('status').textContent = '';
    try {
      const res = await fetch('/next-id');
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      nextId = data.nextId;
      document.getElementById('nextId').className = 'next-id-value';
      document.getElementById('nextId').textContent = nextId;
      document.getElementById('meta').textContent = `${data.total.toLocaleString()} records · highest existing: ${data.highest.toLocaleString()}`;
      document.getElementById('createBtn').disabled = false;
    } catch (e) {
      document.getElementById('nextId').textContent = 'Error';
      document.getElementById('status').className = 'status error';
      document.getElementById('status').textContent = e.message;
    }
  }

  async function createRecord() {
    const engVal     = document.getElementById('engValue').value.trim();
    const deVal      = document.getElementById('deValue').value.trim();
    const descVal    = document.getElementById('descValue').value.trim();
    const commentVal = document.getElementById('commentValue').value.trim();
    if (!engVal) { alert('English string is required.'); return; }
    document.getElementById('createBtn').disabled = true;
    document.getElementById('status').className = 'status';
    document.getElementById('status').textContent = 'Creating record…';
    try {
      const res = await fetch('/create-record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: String(nextId), engValue: engVal, deValue: deVal, descValue: descVal, commentValue: commentVal })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      document.getElementById('status').className = 'status success';
      document.getElementById('status').textContent = `Record ${nextId} created successfully!`;
      document.getElementById('engValue').value = '';
      document.getElementById('deValue').value = '';
      document.getElementById('descValue').value = '';
      document.getElementById('commentValue').value = '';
      refresh();
    } catch (e) {
      document.getElementById('status').className = 'status error';
      document.getElementById('status').textContent = e.message;
      document.getElementById('createBtn').disabled = false;
    }
  }

  refresh();
</script>
</body>
</html>"""
HTML = HTML.replace("__VIEW_ID__", VIEW_ID)


def fetch_all_records():
    all_ids = []
    offset = 0
    limit = 1000
    while True:
        params = urllib.parse.urlencode({"page": json.dumps({"offset": offset, "limit": limit})})
        url = f"https://api.gridly.com/v1/views/{VIEW_ID}/records?{params}"
        req = urllib.request.Request(url, headers={"Authorization": f"ApiKey {API_KEY}"})
        with urllib.request.urlopen(req) as res:
            records = json.loads(res.read())
        ids = [int(r["id"]) for r in records if r["id"].isdecimal()]
        all_ids.extend(ids)
        if len(records) < limit:
            break
        offset += limit
    return all_ids


def create_gridly_record(record_id, eng_value, de_value="", desc_value="", comment_value=""):
    url = f"https://api.gridly.com/v1/views/{VIEW_ID}/records"
    cells = [
        {"columnId": "ENG", "value": eng_value},
        {"columnId": "OurRecordID", "value": int(record_id)},
    ]
    if de_value:
        cells.append({"columnId": "GER", "value": de_value})
    if desc_value:
        cells.append({"columnId": "Description", "value": desc_value})
    if comment_value:
        cells.append({"columnId": "Comment", "value": comment_value})
    payload = json.dumps([{"id": record_id, "cells": cells}]).encode()
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"ApiKey {API_KEY}",
        "Content-Type": "application/json"
    }, method="POST")
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress server logs

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif self.path == "/next-id":
            try:
                all_ids = fetch_all_records()
                if not all_ids:
                    self.send_json({"nextId": 1, "highest": 0, "total": 0})
                    return
                highest = max(all_ids)
                self.send_json({"nextId": highest + 1, "highest": highest, "total": len(all_ids)})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/create-record":
            try:
                length = int(self.headers["Content-Length"])
                body = json.loads(self.rfile.read(length))
                create_gridly_record(
                    str(body["id"]),
                    body["engValue"],
                    body.get("deValue", ""),
                    body.get("descValue", ""),
                    body.get("commentValue", "")
                )
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("localhost", 0), Handler)
    port = server.server_address[1]
    url = f"http://localhost:{port}"
    print(f"Starting Gridly Tool at {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
