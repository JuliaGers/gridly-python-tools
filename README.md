# Gridly Python Tools

A small collection of Python scripts for working with the [Gridly](https://gridly.com) API. No third-party packages required — only Python's standard library.

---

## Tools

### `Find_Free_GridlyID.py`
Fetches all records from your Gridly view, finds the highest existing numeric Record ID, and copies the next available ID to your clipboard.

**Run:** Double-click the file, or `python Find_Free_GridlyID.py`

---

### `Create_Gridly_String.py`
Opens a browser-based UI for creating new string records. Automatically calculates the next available Record ID and lets you fill in English, German, Description, and Comment fields before submitting directly to Gridly.

**Run:** Double-click the file, or `python Create_Gridly_String.py`
Press `Ctrl+C` in the terminal to stop the local server.

---

### `Search_Gridly.py`
Loads all records from your Gridly view into memory and lets you run fast, repeated keyword searches across all columns from the terminal.

**Run:** Double-click the file, or `python Search_Gridly.py`
Press `Enter` with no input to quit.

---

## Setup

### 1. Install Python
Download from [python.org/downloads](https://www.python.org/downloads/).
On Windows, check **"Add Python to PATH"** during installation.

### 2. Configure your credentials
Copy `.env.example` to `.env` in the same folder and fill in your values:

```
API_KEY=your_gridly_api_key_here
VIEW_ID=your_gridly_view_id_here
```

> **Note:** Never commit your `.env` file. It is excluded by `.gitignore`.

### 3. Run a script
Double-click any `.py` file to run it, or open a terminal and run:
```
python Find_Free_GridlyID.py
```

---

## Requirements
- Python 3.6+
- No additional packages needed
