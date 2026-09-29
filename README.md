# Syntra V2

Syntra V2 is a multimodal lecture reconstruction, evidence-grounded study, and collaborative learning platform.

## Features
- Multimodal Lecture Processing (Audio, Images, PDF, Text)
- Evidence Extraction and Alignment
- Fused Concept Generation
- Shared Q&A with Evidence Tracing
- Conflict Resolution for Admins

## Tech Stack
- Frontend: Streamlit
- Backend: Python
- AI: Google Gemini (via google-genai)
- Database: PostgreSQL (via SQLAlchemy)

## Setup
1. Create virtual environment
2. Copy `.env.example` to `.env`
3. Configure settings
4. Run migrations: `alembic upgrade head`
5. Run application: `streamlit run app.py`
