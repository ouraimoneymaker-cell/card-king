# CodKing

**CodKing** is a **decision engine** for trading card collectors (sports cards + TCG).  
It turns card data into a clear recommendation: **GRADE / SELL / HOLD / BUY / PASS**.

This is **not** a social network and **not** a basic collection tracker. The product exists to reduce uncertainty and help collectors make fast, confident decisions.

---

## What CodKing solves

Collectors constantly face decision overload:

- Is this card worth grading?
- What grade is it likely to get?
- Will grading actually make profit after fees?
- Is now the right time to sell or hold?
- Is this card underpriced or overpriced?

CodKing answers those questions with a single, simple decision output.

---

## MVP scope (minimum features)

### 1) Card input
- Scan with camera **or** manual search entry
- Identify card via lookup

### 2) Market value estimate
- Estimate value from recent sold-market signals (e.g., sold comps logic)

### 3) Grade probability estimate
- Initial grading estimator (simple model to start)
- Output grade probability ranges (ex: “PSA 9 likely”, “PSA 10 chance: low/med/high”)

### 4) ROI calculator
- Include grading fees + shipping (configurable)
- Output expected profit/loss range

### 5) Decision output (core)
Return one recommendation:

- **GRADE**
- **SELL**
- **HOLD**
- **BUY**
- **PASS**

Include:
- Confidence score
- Risk level
- Short explanation (plain English)

---

## UX rules

- Mobile-first
- Dark theme
- Serious, professional tone (financial-tool vibe)
- Minimal steps, fast results
- One main “Decision” screen

---

## Non-goals (explicitly out of scope for MVP)

- Marketplace / escrow shipping
- Social network / chat / forums
- Full inventory accounting / taxes
- Long analytics dashboards

---

## Tech approach (recommended)

CodKing can be built as a web app first (mobile-first UI), then wrapped as a native app later.

Suggested baseline:
- Backend: FastAPI (Python)
- Frontend: simple static UI or React (choose one and keep it minimal)
- Storage: SQLite initially, upgrade later
- Deployment: Render

---

## Local development (template)

> Update these commands to match the actual repo once the scaffold exists.

1. Create and activate a virtual environment
2. Install dependencies
3. Run the app
4. Confirm health endpoint works

Expected health response:

```json
{"status":"ok"}
