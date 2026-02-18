# Card King (MVP)

Card King is a **decision engine** for trading card collectors. It outputs a clear call:
**GRADE / SELL / HOLD / BUY / PASS** with confidence, risk, and a short explanation.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

