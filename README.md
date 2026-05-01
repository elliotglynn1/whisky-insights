# whisky-insights

## Workflow Summary

- **Extract:** `whisky_api.py` fetches data.  
- **Load:** `ingest.py` saves it into `whisky_data.db`.  
- **Display:** `main.py` reads the DB and shows the dashboard.  

This separation ensures that if the API changes, you only have to fix one file (`whisky_api.py`) without breaking your entire dashboard.

---

## 1. Installation

Open your terminal and run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 2. Verify

Restart your terminal and run:

```bash
uv --version
```

---

## 3. Usage for this project

Instead of using `pip`, you can use `uv` for much faster setup:

- Create environment:
  ```bash
  uv venv
  ```

- Activate environment:
  ```bash
  source .venv/bin/activate
  ```

- Install requirements:
  ```bash
  uv pip install streamlit polars plotly
  ```

---

## 4. Updating

To update `uv` in the future:

```bash
uv self update
```
