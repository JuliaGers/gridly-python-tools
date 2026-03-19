# Gridly Search

A Python script for searching the [Gridly](https://gridly.com) API. No third-party packages required — only Python's standard library.

---

## Tool

### `Search_Gridly.py`
Loads all records from your Gridly view into memory and lets you run fast, repeated keyword searches across all columns from the terminal. Supports searching by text string or Record ID — searching by ID shows all translations for that record. Searching for a text string shows all records with search hits.


---

## Setup

### Configure your credentials
Create a `.env` file in the same folder as the script with the following:

```
API_KEY=your_gridly_api_key_here
VIEW_ID=your_gridly_view_id_here
```


## Requirements
- Python 3.6+
- No additional packages needed
