# HiddenGem Backend

This folder contains the Python + FastAPI backend.

## Setup

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy env file and fill in values
copy ..\\.env.example .env      # Windows
# cp ../.env.example .env       # macOS/Linux

# 5. Run the dev server
uvicorn main:app --reload --port 8000
```

API docs will be at http://localhost:8000/docs
