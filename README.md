# Krushi Yantra — Carbon Credit Farm Management System

A production-ready **FastAPI** application for carbon credit farm management with AI assistant, voice interaction, gamified plant discovery, geospatial features, JWT authentication, and Neo4j graph database integration.

---

## 🎯 Project Overview

Krushi Yantra enables Indian farmers to register their farms, calculate carbon credits, interact with an agriculture-specific AI assistant (powered by Sarvam AI), and gamify plant discovery — all through a secure, async web application.

### Core Features

| Feature | Description |
|---|---|
| 🔐 **JWT Authentication** | Secure token-based user auth with bcrypt passwords |
| 🌾 **Farm Management** | CRUD for farms with geospatial polygon data |
| 📊 **Carbon Credits** | Dynamic calculation by soil type, area, and verification status |
| 🤖 **AI Assistant** | Sarvam LLM with per-user mem0 memory, voice STT/TTS, conversation history |
| 🌿 **Plant Discovery** | PlantNet identification, hexagonal badges, growing tree, daily streaks |
| 🗺️ **Geospatial** | Polygon-based farm boundaries with area calculation |
| 👥 **User Profiles** | Profile management with points and rankings |
| 📈 **Leaderboard** | Real-time farmer rankings |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Frontend Layer                          │
│   Jinja2 Templates │ Vanilla CSS/JS │ SVG Animations         │
└─────────────────────────────┬────────────────────────────────┘
                              │ HTTP / REST / Multipart
┌─────────────────────────────▼────────────────────────────────┐
│                    Application Layer (FastAPI)                 │
│   auth │ users │ leaderboard │ farmservice │ aihelp │ challenge│
└──────┬──────────┬──────────────────────────┬─────────────────┘
       │          │                          │
┌──────▼──┐  ┌───▼──────────────┐  ┌────────▼────────────────┐
│ SQLite/ │  │   External APIs   │  │   AI/ML Services        │
│PostgreSQL│  │  PlantNet (STT)  │  │  Sarvam LLM + STT/TTS  │
│  Neo4j  │  │  Qdrant (vector) │  │  mem0 memory            │
└─────────┘  └──────────────────┘  └─────────────────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI** — Async web framework
- **SQLAlchemy 2.0** — Async ORM with `Mapped[]` declarative models
- **Pydantic v2** — Data validation and settings
- **JWT (python-jose)** — Token-based authentication
- **Passlib (bcrypt)** — Password hashing
- **httpx** — Async HTTP client for external APIs

**AI / ML:**
- **Sarvam AI** (`sarvam-m`) — Agriculture-restricted LLM
- **Sarvam STT** (`saarika:v2`) — Speech-to-text for voice chat
- **Sarvam TTS** (`bulbul:v1`) — Text-to-speech voice responses
- **mem0** — Per-user persistent memory across conversations
- **PlantNet API** — Plant species identification from photos

**Databases:**
- **SQLite** (dev) / **PostgreSQL** (prod) — Relational data
- **Neo4j Aura** — Graph database for farm relationships
- **Qdrant** — Vector database (optional, read-only knowledge retrieval)

**Frontend:**
- **Jinja2** — Server-side templating
- **Vanilla CSS** — Fredoka One + Nunito fonts, retro green palette
- **JavaScript (ES6+)** — Fetch API, MediaRecorder (voice), SVG animations

---

## 📁 Project Structure

```
baseprogram/
├── main.py                     # FastAPI app, lifespan, router registration
├── database.py                 # Async engine, AsyncSession, Base
├── auth.py                     # JWT creation, verification, get_current_user
├── config.py                   # Pydantic Settings (reads from .env)
│
├── models/
│   ├── user.py                 # User ORM model
│   ├── farm.py                 # Farm with polygon + carbon credits
│   ├── conversation.py         # AI chat: Conversation + Message
│   └── plant_discovery.py      # PlantDiscovery, DailyStreak, UserTree
│
├── schemas/
│   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   ├── farm.py                 # FarmCreate, FarmUpdate, FarmResponse
│   ├── aihelp.py               # ChatRequest, ChatResponse, ConversationOut
│   └── plant.py                # PlantIdentifyResponse, BadgeOut, StreakResponse
│
├── routers/
│   ├── auth.py                 # /api/auth/* — register, login
│   ├── users.py                # /api/users/* — profile CRUD
│   ├── leaderboard.py          # /api/leaderboard
│   ├── farmservice.py          # /farmservice + /api/farmservice/*
│   ├── aihelp.py               # /aihelp — AI chat + voice endpoints
│   └── challenge.py            # /challenge — plant discovery + streaks
│
├── clients/
│   └── sarvam_client.py        # Sarvam LLM, STT (saarika:v2), TTS (bulbul:v1)
│
├── services/
│   ├── ai_service.py           # AI pipeline: retrieval → memory → LLM → store
│   ├── memory_service.py       # mem0 wrapper (graceful fallback)
│   ├── retrieval_service.py    # Qdrant vector retrieval (QDRANT_ENABLED flag)
│   ├── plant_ai_service.py     # Plant fun facts + plant-specific chat
│   ├── plantnet_service.py     # PlantNet API + emoji/badge color assignment
│   └── streak_service.py       # Async daily streak + tree growth logic
│
├── utils/
│   ├── carbon_calculator.py    # Credit formula by soil type + verification
│   └── geospatial.py           # Haversine area, polygon centroid
│
├── templates/
│   ├── base.html               # Navbar, fonts, common structure
│   ├── home.html               # Landing page
│   ├── dashboard.html          # User dashboard + 🔥 streak widget
│   ├── farmservice.html        # Farm management
│   ├── aihelp.html             # AI chat + voice orb panel
│   └── challenge.html          # Plant discovery, tree, badges
│
├── static/
│   ├── css/
│   │   ├── aihelp.css          # 3-panel chat layout
│   │   └── challenge.css       # Tree section, hex badges, modal steps
│   └── js/
│       ├── auth.js             # Token management, requireAuth
│       ├── farmservice.js      # Farm CRUD
│       ├── aihelp.js           # Chat + voice: MediaRecorder, orb states
│       └── challenge.js        # Tree SVG, streak strip, badge grid, upload modal
│
├── .env                        # All secrets and API keys (never commit)
└── pyproject.toml              # uv dependencies
```

---

## 🗄️ Database Schema

### Tables

| Table | Purpose |
|---|---|
| `users` | Farmer profiles with points |
| `farms` | Farm boundaries, soil, carbon credits |
| `conversations` | AI chat session containers |
| `messages` | Individual chat messages |
| `plant_discoveries` | Plant badge collection (text only) |
| `daily_streaks` | Per-day verification records |
| `user_trees` | Virtual growing tree state |

### Key Relationships

```
User ──< Farm
User ──< Conversation ──< Message
User ──< PlantDiscovery
User ──< DailyStreak
User ──1 UserTree
```

### Carbon Credit Formula

```
credits = area_hectares × soil_multiplier × 12.5 base_rate

soil_multiplier: Loamy=1.2 | Clay=1.0 | Sandy=0.8 | Mixed=1.0
verified bonus:  +100% credits when is_verified=True
value_inr = credits × ₹500
```

### Plant Tree Levels

```
Leaves:  0-4  → Level 1
         5-9  → Level 2
         10-14 → Level 3
         ...  (every 5 plants = +1 level, max Level 10)
```

---

## 🔐 Authentication

JWT Bearer token flow:
1. `POST /api/auth/register` → create account
2. `POST /api/auth/token` → returns `access_token`
3. Store in `localStorage`, include as `Authorization: Bearer <token>` header
4. All protected routes use `Depends(get_current_user)` FastAPI dependency

HTML page routes use client-side JS auth guard (redirect to `/login` if no token).

---

## 🤖 AI Assistant Architecture

### Text Pipeline
```
User message
   → Qdrant retrieval (if QDRANT_ENABLED=true)
   → mem0 memory recall
   → User profile context from DB (name, farms, location)
   → Sarvam LLM (sarvam-m, agriculture-restricted prompt)
   → Store in DB + mem0
   → Response
```

### Voice Pipeline
```
Mic audio (WebM/WAV)
   → POST /aihelp/voice/chat (multipart)
   → Sarvam STT saarika:v2 → transcript
   → Text pipeline above
   → Sarvam TTS bulbul:v1 → WAV bytes
   → Browser plays audio
```

### Agriculture Restriction

The assistant **only answers questions about**: farming, crops, carbon credits, soil, irrigation, government schemes, pest control, livestock. Off-topic questions (coding, math, etc.) receive a polite redirect.

---

## 🌿 Plant Discovery System

### Identification Pipeline
```
Upload photo
   → PlantNet API /v2/identify/all (≥30% confidence threshold)
   → Parse: common name, scientific name, family, confidence
   → Sarvam fun fact generation (2 sentences)
   → Check first-global-discovery (bonus 40pts vs 10pts)
   → Save PlantDiscovery record (TEXT ONLY — image not stored)
   → Upsert DailyStreak + UserTree
   → Return badge response
```

### Gamification
- 🏅 **First global discovery** — 40 points + Pioneer banner
- 🌱 **Normal discovery** — 10 points + badge
- 🔄 **Re-discovery** — 5 points, updates fun fact
- 🌲 **Growing tree** — gains a leaf per plant, visible SVG animation
- 🔥 **Daily streak** — 7-day strip on dashboard and challenge page

---

## 🚀 Running the Application

### Prerequisites
- Python 3.11+
- `uv` package manager

### Installation

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env   # then fill in your keys

# Run dev server
uv run fastapi dev main.py
```

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | JWT signing key (generate with `secrets.token_hex(32)`) |
| `SARVAM_API_KEY` | ✅ | Sarvam AI API key |
| `PLANTNET_API_KEY` | ✅ | PlantNet identification API key |
| `MEM0_API_KEY` | ⚪ | mem0 cloud key (empty = local mode) |
| `QDRANT_ENABLED` | ⚪ | `true` to enable vector retrieval (default: `false`) |
| `NEO4J_URI` | ⚪ | Neo4j Aura URI for graph features |
| `GEMINI_API_KEY` | ⚪ | Google Gemini (reserved for future) |

### Access Points

| URL | Description |
|---|---|
| http://localhost:8000 | Landing page |
| http://localhost:8000/farmservice | Farm management |
| http://localhost:8000/aihelp | AI chat + voice assistant |
| http://localhost:8000/challenge | Plant discovery + streaks |
| http://localhost:8000/dashboard | User dashboard |
| http://localhost:8000/docs | Swagger UI (auto-generated) |

---

## 🧪 Quick API Test

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Ravi","username":"ravi","email":"ravi@farm.com","phone":"9876543210","password":"Pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/token \
  -d "username=ravi@farm.com&password=Pass123"

# Chat with AI assistant
curl -X POST http://localhost:8000/aihelp/chat \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What crops grow well in loamy soil?"}'

# Identify a plant
curl -X POST http://localhost:8000/challenge/identify \
  -H "Authorization: Bearer TOKEN" \
  -F "image=@/path/to/plant.jpg"
```

---

## 📦 Key Dependencies

```toml
fastapi, uvicorn[standard]     # Web framework + ASGI server
sqlalchemy[asyncio]            # Async ORM
aiosqlite                      # Async SQLite driver
pydantic[email]                # Data validation
python-jose[cryptography]      # JWT
passlib[bcrypt]                # Password hashing
httpx                          # Async HTTP (Sarvam, PlantNet)
mem0ai                         # Persistent conversation memory
qdrant-client                  # Vector search (optional)
python-multipart               # File upload support
jinja2                         # HTML templating
```

---

## 📝 Commit History Note

All new files added in this session:
- `models/conversation.py`, `models/plant_discovery.py`
- `schemas/aihelp.py`, `schemas/plant.py`
- `clients/sarvam_client.py`
- `services/` — `ai_service`, `memory_service`, `retrieval_service`, `plant_ai_service`, `plantnet_service`, `streak_service`
- `routers/aihelp.py`, `routers/challenge.py`
- `templates/aihelp.html`, `templates/challenge.html`
- `static/css/aihelp.css`, `static/css/challenge.css`
- `static/js/aihelp.js`, `static/js/challenge.js`
