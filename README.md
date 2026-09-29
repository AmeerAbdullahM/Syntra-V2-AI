<div align="center">

<img src="docs/assets/syntra-logo.png" alt="Syntra AI logo" width="560"/>

# Syntra V2

### Multimodal Lecture Reconstruction • Evidence-Grounded Learning • Collaborative Study

<p>
  <b>Turn scattered learning material into a structured, traceable and collaborative learning workspace.</b>
</p>

<p>
  <a href="https://github.com/AmeerAbdullahM/Syntra-V2-AI">Repository</a> ·
  <a href="https://github.com/AmeerAbdullahM/Syntra-V2-AI/issues">Issues</a>
</p>

</div>

---

## Overview

**Syntra V2** is a multimodal learning platform designed to bring lecture material, extracted evidence, synthesized concepts, study artifacts and collaborative discussion into one workspace.

Instead of treating every uploaded file as an isolated document, Syntra organizes learning around **Dens** — collaborative learning spaces — and **Rocks** — structured topic/unit containers inside a Den.

The platform is designed around a simple idea:

> **Learning should be traceable from source material → evidence → concepts → questions → study artifacts.**

Syntra V2 combines a Streamlit interface, a Python service layer, PostgreSQL persistence, and Google Gemini-powered AI workflows.

---

## Why Syntra?

Modern students often learn from a mixture of:

- Lecture recordings
- Images and diagrams
- PDFs and notes
- Text/code files
- Multiple versions of study material
- Peer explanations and discussions

The problem is not simply finding information. The harder problem is **connecting information, identifying conflicting evidence, building a coherent understanding, and revisiting that understanding later**.

Syntra V2 addresses this with a structured learning pipeline:

```mermaid
flowchart LR
    A["Audio / Images / PDFs / Text"] --> B["Material Processing"]
    B --> C["Evidence Extraction"]
    C --> D["Evidence Alignment"]
    D --> E["Concept Fusion"]
    E --> F["Study Artifacts"]
    C --> G["Evidence-Grounded Q&A"]
    G --> H["Collaborative Discussion"]
    D --> I["Conflict Detection"]
    I --> J["Admin Resolution"]
```

---

## Core Features

### 1. Multimodal Material Workspace

Upload and organize learning material inside a structured learning space.

Supported material workflows include:

- Audio
- Images
- PDF documents
- Text-based files
- Source/code files for viewing
- Material status tracking
- Material download and in-browser viewing

Each material is associated with a **Rock**, allowing related resources to be studied together.

---

### 2. Dens — Collaborative Learning Spaces

A **Den** is Syntra's main collaborative workspace.

Users can:

- Create learning Dens
- Make Dens public or private
- Set invite codes for private Dens
- Optionally limit membership
- Request access to public Dens
- Join private Dens using an invite code
- Manage members
- Leave a Den
- Manage pending join requests

This gives students a shared environment instead of isolated personal notes.

---

### 3. Rocks — Structured Learning Units

Inside each Den, learning material is organized into **Rocks**.

A Rock can represent:

- A lecture
- A chapter
- A unit
- A topic
- A module
- Any logical learning section

Each Rock can contain its own materials, evidence, concepts, conflicts and generated artifacts.

---

### 4. Evidence Extraction & Alignment

Syntra separates raw material from the information extracted from it.

The evidence layer can associate extracted content with:

- Source modality
- Confidence
- Learning Rock
- Relationships between evidence items

This creates a traceable foundation for downstream AI synthesis.

```mermaid
flowchart TD
    A["Source Material"] --> B["Extracted Evidence"]
    B --> C{"Confidence"}
    C -->|"High / Strong"| D["Reliable Evidence"]
    C -->|"Lower / Uncertain"| E["Needs Review"]
    D --> F["Concept Fusion"]
    E --> F
```

---

### 5. Conflict Detection & Resolution

When evidence items contradict one another, Syntra can represent the relationship as a conflict.

Admins can:

- Inspect the conflicting source and target evidence
- Review the reasoning associated with the contradiction
- Add a clarification
- Mark the conflict as resolved

This is important for educational material where different sources may present different claims.

```mermaid
flowchart LR
    A["Evidence A"] --> C["Contradiction"]
    B["Evidence B"] --> C
    C --> D["Admin Review"]
    D --> E["Clarification"]
    E --> F["Resolved Evidence Context"]
```

---

### 6. Fused Concept Generation

Once evidence has been collected and aligned, Syntra can run its **Fusion Pipeline**.

The goal is to transform fragmented evidence into higher-level concepts with explanations.

```mermaid
flowchart LR
    A["Multiple Evidence Items"] --> B["Alignment"]
    B --> C["Fusion Pipeline"]
    C --> D["Fused Concepts"]
    D --> E["Explanations"]
```

Admins can trigger fusion for a Rock from the workspace.

---

### 7. AI-Powered Study Artifacts

Syntra can generate study-oriented artifacts from a Rock, including a **Cheat Sheet** workflow.

Generated artifacts are stored in the learning workspace so that students can revisit them without regenerating the content every time.

---

### 8. Evidence-Aware Q&A

Students can ask questions about the material available in a Den.

Example:

> "What are the main takeaways from Unit 1?"

Syntra processes the question through the learning workspace and stores the resulting Q&A thread.

This turns the Den into an interactive study assistant rather than a static document repository.

---

### 9. Role-Based Collaboration

Dens distinguish between **Admins** and **Members**.

Admins can perform workspace-management actions such as:

- Create/delete Rocks
- Upload material
- Trigger fusion
- Generate study artifacts
- Review conflicts
- Manage join requests
- Remove members
- Ban users
- Delete the Den

Members can access the collaborative learning experience according to their permissions.

---

## Product Architecture

```mermaid
flowchart TB
    U["Student / Admin"] --> UI["Streamlit Frontend"]

    UI --> AUTH["Authentication & Session"]
    UI --> DEN["Den / Rock Workspace"]
    UI --> MAT["Material Management"]
    UI --> QA["Q&A"]
    UI --> FUSION["Fusion & Artifact Workflows"]

    DEN --> DB["PostgreSQL"]
    MAT --> DB
    QA --> DB
    FUSION --> DB

    MAT --> STORAGE["Local / Object Storage"]
    MAT --> AI["Google Gemini"]
    QA --> AI
    FUSION --> AI

    MIG["Alembic"] --> DB
```

### High-Level Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Application | Python |
| AI | Google Gemini via `google-genai` |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation / Settings | Pydantic + Pydantic Settings |
| Authentication | Custom auth + JWT/Authlib support |
| Password Security | Passlib / bcrypt / Argon2 |
| Storage | Local storage with object-storage configuration |
| Container Support | Docker Compose |
| Testing | Pytest |

---

## Repository Structure

```text
Syntra-V2-AI/
│
├── alembic/                     # Database migration scripts
│
├── backend/
│   ├── config/                  # Application settings
│   ├── database/                # DB connection, models and repositories
│   ├── models/                  # SQLAlchemy data models
│   ├── schemas/                 # Pydantic schemas
│   └── services/
│       ├── auth/                # Authentication
│       ├── den/                 # Learning-space management
│       ├── rock/                # Rock/topic management
│       ├── material/            # Material handling
│       ├── qa/                  # Q&A workflows
│       └── artifact/            # Study-artifact generation
│
├── frontend/
│   ├── app.py                   # Main Streamlit application
│   ├── pages/                   # Dashboard and workspace pages
│   ├── assets/                  # UI assets
│   ├── session.py               # Session/auth state
│   ├── styles.py                # Syntra UI styling
│   └── universe.py              # UI visual layer
│
├── scripts/                     # Utility / worker scripts
├── workers/                     # Background processing workers
├── tests/
│   └── unit/                    # Unit tests
│
├── syntra_v2_test_dataset/      # Test/sample dataset
├── app.py                       # Root application launcher
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml           # PostgreSQL development service
├── pyproject.toml               # Python project configuration
└── requirements.txt             # Python dependencies
```

---

## Getting Started

### Prerequisites

Make sure you have:

- Python **3.10+**
- PostgreSQL 15+ or Docker
- A Google Gemini API key
- Git

---

### 1. Clone the repository

```bash
git clone https://github.com/AmeerAbdullahM/Syntra-V2-AI.git
cd Syntra-V2-AI
```

---

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Start PostgreSQL

The repository includes a Docker Compose configuration for PostgreSQL.

```bash
docker compose up -d db
```

The development database is configured as:

```text
Host: localhost
Port: 5432
Database: syntra_v2
User: postgres
Password: password
```

> For production, replace development credentials with secure secrets.

---

### 5. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/syntra_v2

GEMINI_API_KEY=your_gemini_api_key

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

SESSION_SECRET=replace-with-a-secure-secret

STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./data/storage

OBJECT_STORAGE_BUCKET=
OBJECT_STORAGE_ENDPOINT=
OBJECT_STORAGE_ACCESS_KEY=
OBJECT_STORAGE_SECRET_KEY=

SUPERADMIN_EMAIL=
SUPERADMIN_PASSWORD=
```

**Never commit real API keys, passwords or session secrets to Git.**

---

### 6. Run database migrations

```bash
alembic upgrade head
```

---

### 7. Start Syntra

From the repository root:

```bash
streamlit run app.py
```

The root launcher starts the Streamlit frontend located under `frontend/`.

---

## Typical User Flow

```mermaid
sequenceDiagram
    actor Student
    participant UI as Syntra UI
    participant DB as PostgreSQL
    participant AI as Gemini

    Student->>UI: Create / Join Den
    UI->>DB: Store membership
    Student->>UI: Create / Enter Rock
    Student->>UI: Upload learning material
    UI->>DB: Store material metadata
    UI->>AI: Process / extract learning information
    AI-->>UI: Evidence
    UI->>DB: Store evidence
    Student->>UI: Ask question
    UI->>AI: Generate grounded response
    AI-->>UI: Answer
    UI->>DB: Store Q&A thread
```

---

## Security Considerations

Syntra includes several application-level security mechanisms, including:

- Password hashing
- Session-based authentication
- Role-aware workspace actions
- Private Den invite codes
- Member management
- Ban/remove controls
- Environment-based secret configuration

For production deployment:

1. Replace all development credentials.
2. Generate a strong session secret.
3. Keep Gemini and OAuth credentials outside source control.
4. Use a managed/secured PostgreSQL instance.
5. Configure durable object storage for uploaded material.
6. Run behind HTTPS.
7. Review authorization rules before exposing the application publicly.

---

## Development

### Run tests

```bash
pytest
```

The project is configured to discover tests under:

```text
tests/
```

with files following:

```text
test_*.py
```

### Database migrations

Create a migration after model changes:

```bash
alembic revision --autogenerate -m "describe your change"
```

Then apply it:

```bash
alembic upgrade head
```

---

## Design Philosophy

Syntra V2 is built around five principles:

### 1. Multimodal

Learning does not happen from text alone. Different source types should contribute to the same learning context.

### 2. Traceable

AI-generated understanding should have a relationship with the evidence from which it was derived.

### 3. Collaborative

Learning spaces should support students, peers and administrators together.

### 4. Structured

Instead of one giant chat history, learning is organized into Dens → Rocks → Materials → Evidence → Concepts.

### 5. Reviewable

When sources disagree, the system should expose the disagreement rather than silently hiding it.

---

## Syntra's Learning Model

```text
DEN
│
├── ROCK
│   │
│   ├── Materials
│   │   ├── Audio
│   │   ├── Images
│   │   ├── PDFs
│   │   └── Text / Code
│   │
│   ├── Evidence
│   │   ├── Extracted content
│   │   ├── Modality
│   │   └── Confidence
│   │
│   ├── Conflicts
│   │   └── Admin resolution
│   │
│   ├── Concepts
│   │   └── Fused explanations
│   │
│   └── Artifacts
│       └── Cheat sheets / study outputs
│
├── Q&A
│   └── Collaborative question threads
│
└── MEMBERS
    ├── Admins
    └── Members
```

---

## Roadmap

Potential areas for future development:

- [ ] Richer evidence citation UI
- [ ] More generated study artifacts
- [ ] Advanced semantic search across Dens
- [ ] Better multimodal processing pipelines
- [ ] Real-time collaborative discussions
- [ ] Background job monitoring
- [ ] Object-storage-first deployment
- [ ] Production deployment configuration
- [ ] Expanded automated test coverage
- [ ] Analytics for learning progress

---

## Contributing

Contributions are welcome.

A simple workflow:

```bash
git checkout -b feature/your-feature
```

Make your changes, add tests where appropriate, then:

```bash
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

Open a pull request with:

- What changed
- Why it changed
- How it was tested
- Screenshots for UI changes, when applicable

---

## Project Status

**Syntra V2 is an active development project.**

The current repository contains the core application structure for multimodal material management, collaborative learning Dens, evidence handling, concept fusion, conflict management, study artifacts and AI-assisted Q&A.

APIs, workflows and UI components may continue to evolve.

---

## License

This project is licensed under the **MIT License**.

---

<div align="center">

### Syntra V2

**From scattered material to structured understanding.**

Built with Python · Streamlit · PostgreSQL · Google Gemini

</div>
