# Gridly Python Tools

A Python script for searching the [Gridly](https://gridly.com) API. No third-party packages required — only Python's standard library.

---

## Tool

### `Search_Gridly.py`
Loads all records from your Gridly view into memory and lets you run fast, repeated keyword searches across all columns from the terminal. Supports searching by text string or Record ID — searching by ID shows all translations for that record.

**Run:** Double-click the file, or `python Search_Gridly.py`
Press `Enter` with no input to quit.

---

## Setup

### 1. Install Python
Download from [python.org/downloads](https://www.python.org/downloads/).
On Windows, check **"Add Python to PATH"** during installation.

### 2. Configure your credentials
Create a `.env` file in the same folder as the script with the following:

```
API_KEY=your_gridly_api_key_here
VIEW_ID=your_gridly_view_id_here
```

> **Note:** Never commit your `.env` file. It is excluded by `.gitignore`.

### 3. Run the script
Double-click `Search_Gridly.py` to run it, or open a terminal and run:
```
python Search_Gridly.py
```

---

## Requirements
- Python 3.6+
- No additional packages needed
