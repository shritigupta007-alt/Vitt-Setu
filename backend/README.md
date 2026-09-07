# VittSetu backend

The service is intentionally stateless. It accepts only derived financial
features, returns deterministic decision-support output, and writes nothing to
a database or browser session.

## Run locally

From this directory, create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation.

Run tests and linting with:

```powershell
pytest
ruff check .
```

## API summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health and artifact versions |
| `GET` | `/api/personas` | Synthetic demo personas and derived features |
| `POST` | `/api/score` | Deterministic readiness score and explanation |
| `GET` | `/api/lenders/search?q=` | Illustrative registry search |
| `GET` | `/api/model-card` | Features, weights, limitations, and provenance |

`/api/score` rejects requests without an explicit consent acknowledgement. This
is a product-flow guardrail rather than a substitute for production consent
management.

## Example score request

```json
{
  "consent_acknowledged": true,
  "intended_use": "inventory",
  "features": {
    "inflow_regularity": 0.82,
    "income_volatility": 0.28,
    "bill_punctuality": 0.9,
    "supplier_payment_consistency": 0.78,
    "balance_buffer_days": 14,
    "data_coverage_months": 6
  }
}
```

## CORS

The default allowed frontend origins are `http://localhost:5173` and
`http://127.0.0.1:5173`. Override them with a comma-separated `ALLOWED_ORIGINS`
environment variable when deploying the frontend.
