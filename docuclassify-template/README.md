# DocuClassify — Django Cascading Classifier & RBAC Starter

A production-shaped Django starter for building **document intelligence / audit / compliance SaaS tools** — the kind of project that normally takes weeks to scaffold correctly. This template gives you a working foundation for:

- **Cascading document classification**: Regex rules → TF-IDF/Logistic Regression → Claude API fallback (only pay for API calls on genuinely ambiguous documents)
- **Role-based access control (RBAC)**: custom user model with roles (admin, auditor, reviewer, viewer) baked in from day one — no painful `AUTH_USER_MODEL` migration later
- **PostgreSQL configured correctly**, with the common local-auth pitfall fixed (see below)
- A working dashboard showing classification breakdown by category and by which tier handled each document
- Clean, documented, ready to extend — not a toy demo

## Tech Stack
Django 5 · PostgreSQL · Scikit-learn · Claude API · Bootstrap 5

## What this template is *for*
Use this as the base for: audit/compliance platforms, invoice/contract processing tools, document intelligence dashboards, or any SaaS where you need to classify incoming documents cheaply and accurately at scale.

---

## Setup

### 1. Clone and create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up PostgreSQL
Create the database and user:
```sql
CREATE DATABASE docuclassify;
CREATE USER postgres_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE docuclassify TO postgres_user;
```

**Common gotcha (this trips almost everyone up on Windows/local setups):**
If you get `FATAL: password authentication failed for user "postgres"`, it's almost always one of these:
1. Your `.env` password doesn't match what you set in `psql` — they must match exactly.
2. Your PostgreSQL `pg_hba.conf` has the auth method set to `peer` or `scram-sha-256` in a way that conflicts with password auth. Open `pg_hba.conf` and make sure the line for `local`/`127.0.0.1` connections uses `md5`:
   ```
   host    all             all             127.0.0.1/32            md5
   ```
   Then restart PostgreSQL (`sudo service postgresql restart` on Linux, or restart the service on Windows).
3. If you changed the password after the user already existed, run:
   ```sql
   ALTER USER postgres_user WITH PASSWORD 'your_password';
   ```

### 3. Configure environment variables
```bash
cp .env.example .env
```
Fill in your `DB_*` values and (optionally) your `ANTHROPIC_API_KEY` — the app runs fine without it, it'll just fall back to `"other"` for documents that reach Tier 3.

### 4. Run migrations and create a superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. (Optional) Seed demo users for each role
```bash
python manage.py seed_demo_data
```
Creates `demo_admin`, `demo_auditor`, `demo_reviewer`, `demo_viewer` — all with password `demo1234`.

### 6. Train the Tier-2 classifier
The ML model auto-trains on first use with a small sample dataset (`apps/classifier/ml_classifier.py`). Replace `SAMPLE_TRAINING_DATA` with your own labeled examples (aim for 50+ per category) before using this in anything real.

### 7. Run the server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/login/`

---

## How the cascading classifier works

```
Document text
     │
     ▼
Tier 1: Regex rules (apps/classifier/rules.py)
   ├── Match found → return category, confidence 0.99
     ▼
Tier 2: TF-IDF + Logistic Regression (apps/classifier/ml_classifier.py)
   ├── Confidence ≥ threshold (default 0.65) → return category
     ▼
Tier 3: Claude API (apps/classifier/llm_classifier.py)
   └── Returns best-guess category, confidence 0.85
```

This pattern keeps the majority of documents handled by free, fast tiers, and reserves API cost for the genuinely ambiguous cases. The `classified_tier` field on every `Document` lets you track exactly how much volume each tier is handling — useful for monitoring cost and tuning your threshold.

Orchestration lives in `apps/classifier/pipeline.py` — this is the file to read first.

## Text extraction
`apps/documents/text_extraction.py` reads actual file content before classification:
- **PDFs**: extracted with `pdfplumber`. If a PDF is scanned/image-based and has no extractable text layer, it currently falls back to the filename — see the commented OCR fallback in that file if you want to wire up `pdf2image` + `pytesseract` for scanned PDFs (requires `poppler-utils` installed on the host).
- **Images** (png/jpg/tiff/bmp): OCR'd directly with `pytesseract`. Requires the `tesseract-ocr` binary installed on your system (not just the Python package) — `sudo apt install tesseract-ocr` on Linux, or the equivalent for your OS.
- **Spreadsheets** (.xlsx): read with `openpyxl`, all cell text concatenated.
- **.txt**: read directly.
- Any other format, or any extraction failure: falls back to the filename so the pipeline never crashes on an unsupported/corrupt upload.

## Extending this template
- **Add a document category**: add patterns to `apps/classifier/rules.py`, retrain the ML model with labeled examples for the new category, update `CATEGORIES` in `llm_classifier.py`
- **Add a new role**: extend the `Role` choices in `apps/accounts/models.py`, run a migration
- **OCR for scanned PDFs**: see the commented fallback in `apps/documents/text_extraction.py`
- **Multi-tenant isolation**: the `User.organization` field is a starting point — for true tenant isolation, filter all querysets by organization and consider row-level security in PostgreSQL

## License
MIT — use this for personal or commercial projects. Attribution appreciated but not required.
