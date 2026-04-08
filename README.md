# Student Portal - Real-Time Dynamic Intent System

A production-ready student portal with **REAL-TIME DYNAMIC INTENT SYSTEM**, RAG/FAISS vector search, lightweight SLM intent classification, and auto-discoverable database columns.

## 🎯 Key Features

✅ **Real-Time Dynamic Intent System** — Loads DB columns at request-time; supports unlimited query variations  
✅ **24 Queryable Columns** — All columns auto-discovered and auto-intent-generated  
✅ **RAG Pipeline** — FAISS vector index + semantic search for FAQ/document retrieval  
✅ **SLM Intent Classifier** — Lightweight intent classification without heavy models  
✅ **JWT Authentication** — Secure session management with 15-minute tokens  
✅ **200+ Student Records** — Pre-populated with realistic data  
✅ **Dataset Agnostic** — Switch datasets by changing 4 config lines  

## 📦 Prerequisites

- **Python 3.10+**  
- Virtual environment: `venv/` (included) or create one
- No internet required for core functionality

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Install dependencies (one-time, skip on re-runs)
python -m pip install -r requirements_full.txt

# 2. Initialize database and seed students (one-time)
python database_init.py
python setup_students.py

# Step 3: Sync Excel columns to database (if you added new columns)
python sync_excel_db.py

# Step 4: Populate database with realistic data for all columns
python populate_realistic_data.py

# 5. Start the server
python app.py
```

Open **http://localhost:8000** and login with:
- **Username:** `DEMO001`
- **Password:** `demo@123`

### Restart / Re-run (No Reinstall)

```bash
# Stop any running Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start the server
python app.py
```

## 📁 Project Structure

```
project_final/
├── app.py                          # Main FastAPI app (Real-Time Dynamic System)
├── config.py                       # Centralized config (update for new datasets)
├── realtime_dynamic.py             # Real-Time Dynamic Intent Processor
├── auth/                           # JWT & password utilities
├── templates/                      # HTML/CSS/JS UI
├── stage4/                         # RAG pipeline (FAISS, embeddings)
│   ├── build_index.py
│   ├── rag_pipeline.py
│   └── chat.py
├── embedding_intent_classifier.py  # Intent classification
├── slm_intent_model.py             # Lightweight SLM
├── faq_index.faiss                 # FAISS vector index
├── faq_docs.pkl                    # FAQ documents
├── tfidf_vectorizer.pkl            # TF-IDF vectorizer
├── students_2024.db                # SQLite database (24 columns, 200 students)
├── student_dataset.xlsx            # Excel export
├── student_dataset_extended.csv    # CSV export
└── requirements_full.txt            # Pinned dependencies
```

## ✨ What's New in v2 (Feb 2026)

**🚀 Improved Intent Matching:**
- Semantic similarity matching (not just keywords)
- Handles 20+ variations of same question
- Synonym dictionary (CGPA = GPA = grades = marks)
- Confidence-based response accuracy

**📊 Auto-Detection of New Columns:**
- Add columns to Excel → Auto-syncs to database
- No SQL needed, fully generic
- Works with ANY dataset structure

**⚙️ Better Excel ↔ Database Sync:**
- Two-way synchronization
- Preserves Excel formatting
- Auto-adds new columns to database

---

## 🎮 Using the System

### Web Interface

The UI uses a **dark neon gradient theme** with teal/cyan accents (think futuristic metaverse dashboard). It loads space‑age fonts (Orbitron and Rajdhani) and FontAwesome icons; the dashboard includes a floating sidebar with animated icons and gradient diagonal header flare. Login page has a rotating gradient overlay and particle background while chat bubbles feature avatars, timestamps, and gradient neon colours. Glass‑morphic cards, neon outlines, rotating backgrounds, and micro‑animations on buttons and inputs all contribute to a polished futuristic UX. Colours are defined with CSS variables (`--bg-start`, `--accent1`, etc.) so you can tweak the palette easily. Particle animations drift across every page for atmosphere.

1. **Login:** Enter register number + password
2. **Chat:** Ask questions about ANY column - system understands variations:
   
   **Example: CGPA (understands 20+ ways):**
   - "What's my CGPA?"
   - "Show my GPA"
   - "What are my marks?"
   - "How is my grade?"
   - "Tell me my score"
   - "My performance?"
   - ... and many more!
   
   **Other Examples:**
   - "Contact number?" → Contact_Number
   - "Phone please" → Contact_Number  
   - "Blood type?" → Blood_Group
   - "Internship status" → Internship_Status
   - "Where do I live?" → Hostel_Room

### API Endpoints (with token)

```bash
# Get schema (all columns)
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/schema

# Get all possible intents
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/intents

# Get sample queries
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/all-queries

# Send chat query
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is my GPA?"}' \
  http://localhost:8000/api/chat
```

## 🔧 Configuration

Edit `config.py` to use a different dataset:

```python
class DatasetConfig:
    DATABASE_PATH = "my_database.db"      # SQLite file
    DATA_TABLE = "students"               # Table name
    USER_ID_COLUMN = "StudentID"          # Unique identifier
    USER_NAME_COLUMN = "StudentName"      # Display name
```

No code changes needed — all columns auto-discovered and auto-queryable!

## 🎓 Real-Time Dynamic System

The system loads database columns **on every request** (not at startup):
- Column discovery: `PRAGMA table_info()` executed per request
- Search terms: Auto-generated for each column (e.g., CGPA → cgpa, gpa, grade, score)
- Query matching: Confidence-based (0.95=exact, 0.85=partial, 0.7=word)
- Result: Works with ANY database, unlimited query variations

Example — 24 columns available:
```
Student_Name, Register_Number, Fees_Details, Fees_Status, 
Attendance_Percentage, Books_Borrowed, Scholarship_Eligibility, 
Contact_Number, Email_ID, Date_of_Birth, Faculty, CGPA, 
College_Joining_Date, Major, Emergency_Contact, Guardian_Name, 
Hostel_Room, Transportation_Mode, LinkedIn_Profile, Internship_Status, 
Year_of_Passing, Hobbies, Blood_Group, Nationality
```

## 📊 RAG & SLM Components

### FAISS Vector Index (`stage4/`)
- **File:** `faq_index.faiss`
- **Purpose:** Semantic search for FAQs and documents
- **Usage:** `stage4/rag_pipeline.py`

### SLM Intent Classifier (`slm_intent_model.py`)
- **Purpose:** Lightweight intent classification without heavy LLMs
- **Classifier:** TF-IDF + simple rule-based matching
- **Vectorizer:** `tfidf_vectorizer.pkl`

### Integration
- Main app (`app.py`) uses Real-Time Dynamic processor for column queries
- RAG pipeline available in `stage4/` for document/FAQ retrieval
- Both systems coexist; core app uses Dynamic Intent System

## 📝 Sample Queries (All Work!)

**CGPA:**  
"What's my CGPA?" → Matched: CGPA  
"Show my GPA" → Matched: CGPA  
"What's my grade?" → Matched: CGPA  

**Contact:**  
"Contact number?" → Matched: Contact_Number  
"Phone?" → Matched: Contact_Number  
"How to reach me?" → Matched: Contact_Number  

**New Columns:**  
"Emergency contact" → Matched: Emergency_Contact  
"Internship status" → Matched: Internship_Status  
"Blood group?" → Matched: Blood_Group  
"LinkedIn profile" → Matched: LinkedIn_Profile  
"Hostel room?" → Matched: Hostel_Room  

## 🔐 Authentication

- **JWT Tokens:** 15-minute expiry
- **Password Hashing:** bcrypt (salted)
- **Default Account:** DEMO001 / demo@123
- **Other Accounts:** REG1000–REG1199 with password "student123"

## 🐛 Troubleshooting

**Port 8000 in use:**
```powershell
Get-Process python | Stop-Process -Force
netstat -ano | findstr :8000
```

**Columns not showing:**
```bash
python -c "from app import app; from fastapi.testclient import TestClient; c=TestClient(app); print(c.get('/api/schema').json())"
```

**Database issues:**
```bash
python -c "import sqlite3; conn=sqlite3.connect('students_2024.db'); cur=conn.cursor(); print(list(cur.execute('PRAGMA table_info(students)')))"
```

## 📦 Files Reference

| File | Purpose |
|------|---------|
| `app.py` | FastAPI main app with Real-Time Dynamic system |
| `config.py` | Centralized config (database, table, columns) |
| `realtime_dynamic.py` | Real-Time Dynamic Intent Processor |
| `auth/auth_service.py` | JWT authentication |
| `stage4/rag_pipeline.py` | RAG + FAISS pipeline |
| `slm_intent_model.py` | SLM intent classifier |
| `templates/chat.html` | Chat UI |
| `students_2024.db` | SQLite database (24 cols, 200 students) |
| `student_dataset.xlsx` | Excel export (with new columns) |
| `student_dataset_extended.csv` | CSV export |
| `faq_index.faiss` | FAISS vector index |
| `faq_docs.pkl` | FAQ documents |
| `tfidf_vectorizer.pkl` | TF-IDF model |

## 🎯 Architecture Overview

```
Browser (UI)
    ↓
FastAPI (app.py)
    ├─ /api/auth (JWT login)
    ├─ /api/chat (Real-Time Dynamic Intent Processor)
    ├─ /api/schema (Real-time column discovery)
    ├─ /api/intents (Real-time intent generation)
    ├─ /api/all-queries (Real-time query suggestions)
    └─ /api/user/profile (Student data)
    ↓
RealTimeDynamicProcessor
    ├─ get_all_columns() [PRAGMA table_info()]
    ├─ generate_search_terms()
    ├─ match_column(user_query)
    └─ process_query()
    ↓
SQLite Database (students_2024.db)
    └─ 24 columns × 200 students
```

## Dependencies

See `requirements.txt` for the main packages used in the project (FastAPI,
scikit-learn, FAISS, pandas, numpy, etc.).

## Notes

- If you add or upgrade packages, regenerate `requirements.txt` or create a
   new pinned file with `pip freeze`.
- `requirements_full.txt` — fully pinned environment generated from `provenv`.
- If you want, I can also create `requirements-dev.txt` with test and lint
   tools or generate a fully-pinned `requirements_full.txt` from the venv.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them.
4. Push to your branch and open a pull request.
