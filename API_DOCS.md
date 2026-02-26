# API Documentation — Krushi Yantra

Complete endpoint reference for the Krushi Yantra FastAPI application.

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a JWT Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### `POST /api/auth/register`
Register a new user.

**Body:**
```json
{
  "name": "Ravi Kumar",
  "username": "ravikumar",
  "email": "ravi@farm.com",
  "phone": "9876543210",
  "address": "Pune, Maharashtra",
  "password": "SecurePass123"
}
```
**Response `201`:**
```json
{ "id": 1, "name": "Ravi Kumar", "username": "ravikumar", "email": "ravi@farm.com",
  "phone": "9876543210", "points": 0, "image_path": "/static/profile_pics/default.jpg" }
```
**Errors:** `400` username/email exists · `422` invalid input

---

### `POST /api/auth/token`
Login and receive JWT token.

**Body** (`application/x-www-form-urlencoded`):
```
username=ravi@farm.com&password=SecurePass123
```
**Response `200`:**
```json
{ "access_token": "eyJhbGci...", "token_type": "bearer" }
```
**Errors:** `401` invalid credentials

---

### `POST /api/auth/logout`
Client-side logout (invalidates client token). No auth required.

---

## User Endpoints

### `GET /api/users/me` 🔒
Get current authenticated user profile.

**Response `200`:**
```json
{ "id": 1, "name": "Ravi Kumar", "username": "ravikumar",
  "email": "ravi@farm.com", "phone": "9876543210",
  "address": "Pune", "points": 50, "image_path": "/media/profile_pics/ravi.jpg" }
```

---

### `PATCH /api/users/me` 🔒
Update current user profile.

**Body** (`multipart/form-data`):
```
name=Ravi Kumar Updated
phone=9999999999
photo=<file upload>
```
**Response `200`:** Updated user object

---

### `DELETE /api/users/me` 🔒
Delete current user account and all associated data.

**Response `204 No Content`**

---

### `GET /api/users/{user_id}`
Get public profile by user ID.

**Response `200`:** Public user fields (no email/password)

---

## Farm Service Endpoints

### `GET /api/farmservice/farms` 🔒
List all farms for current user with summary statistics.

**Response `200`:**
```json
{
  "farms": [
    { "id": 1, "farm_name": "Green Valley", "area_hectares": 3.2,
      "soil_type": "Loamy", "district": "Pune", "state": "Maharashtra",
      "annual_credits": 48.0, "annual_value_inr": 24000.0,
      "is_verified": false, "latitude": 18.52, "longitude": 73.85,
      "polygon_coordinates": [[18.52,73.85],[18.53,73.85],[18.53,73.86]],
      "created_at": "2026-02-12T10:00:00" }
  ],
  "summary": {
    "total_farms": 1, "total_area_hectares": 3.2,
    "total_credits": 48.0, "total_value_inr": 24000.0,
    "verified_farms": 0
  }
}
```

---

### `POST /api/farmservice/farms` 🔒
Create a new farm. Area and carbon credits are auto-calculated from polygon.

**Body:**
```json
{
  "farm_name": "Green Valley",
  "phone": "9876543210",
  "district": "Pune",
  "state": "Maharashtra",
  "soil_type": "Loamy",
  "polygon_coordinates": [[18.5204,73.8567],[18.5214,73.8567],[18.5214,73.8577]]
}
```
`soil_type` must be one of: `Loamy` | `Clay` | `Sandy` | `Mixed`

**Response `201`:** Full farm object with calculated `area_hectares`, `annual_credits`, `annual_value_inr`

**Carbon Credit Formula:**
```
credits = area × soil_multiplier × 12.5
soil: Loamy=1.2x  Clay=1.0x  Sandy=0.8x  Mixed=1.0x
value_inr = credits × ₹500
```

---

### `GET /api/farmservice/farms/{farm_id}` 🔒
Get single farm details.

---

### `PUT /api/farmservice/farms/{farm_id}` 🔒
Update farm data. Same body as create (all fields optional).

---

### `DELETE /api/farmservice/farms/{farm_id}` 🔒
Delete a farm. **Response `204`**

---

### `GET /api/farmservice/statistics` 🔒
Aggregated stats for current user's farms.

---

## Leaderboard

### `GET /api/leaderboard`
Public ranking of all users by points.

**Response `200`:**
```json
[{ "rank": 1, "username": "ravikumar", "name": "Ravi Kumar", "points": 150 }]
```

---

## AI Assistant Endpoints (`/aihelp`)

The assistant only answers **agriculture-related** questions (crops, soil, carbon credits, government schemes, pest control, livestock). Off-topic questions receive a polite redirect.

---

### `GET /aihelp`
Serves the AI chat UI page (HTML). Auth enforced client-side.

---

### `POST /aihelp/chat` 🔒
Send a text message to the AI assistant.

**Body:**
```json
{ "message": "What crops grow well in black cotton soil?", "conversation_id": null }
```
Pass `conversation_id` to continue an existing conversation, or `null` to start new.

**Response `200`:**
```json
{
  "response": "Black cotton soil (Vertisol) retains moisture well and is excellent for cotton, sorghum, wheat, and chickpeas...",
  "conversation_id": 5,
  "sources": []
}
```

---

### `POST /aihelp/voice/chat` 🔒
Full voice pipeline: audio → STT → LLM → TTS → WAV audio.

**Body** (`multipart/form-data`):
```
audio=<WAV/WEBM file>
conversation_id=5         (optional)
language=hi-IN            (BCP-47 code, default: hi-IN)
```

**Response `200 audio/wav`** — Raw WAV bytes playable by browser.

Response headers contain:
```
X-Transcript: <transcribed user speech>
X-Response: <assistant text response>
X-Conversation-Id: <conversation id>
```
If TTS fails, falls back to JSON with `{"transcript": ..., "response": ..., "tts_error": ...}`.

**Supported languages:** `hi-IN` | `en-IN` | `kn-IN` | `ta-IN` | `te-IN` | `mr-IN` | `bn-IN` | `pa-IN`

---

### `POST /aihelp/voice/speak` 🔒
TTS only — convert text to WAV audio.

**Body** (`multipart/form-data`):
```
text=Your text to convert (max 500 chars)
language=en-IN
```
**Response `200 audio/wav`**

---

### `GET /aihelp/conversations` 🔒
List all conversations for current user (newest first).

**Response `200`:**
```json
[{ "id": 5, "title": "What crops grow in...", "created_at": "...",
   "messages": [{ "id": 10, "role": "user", "content": "...", "timestamp": "..." }] }]
```

---

### `GET /aihelp/conversations/{id}` 🔒
Get single conversation with all messages.

---

### `DELETE /aihelp/conversations/{id}` 🔒
Delete a conversation and all its messages. **Response `204`**

---

## Plant Discovery Endpoints (`/challenge`)

### `GET /challenge`
Serves the plant discovery page (HTML). Auth enforced client-side.

---

### `POST /challenge/identify` 🔒
Upload a plant photo → identify with PlantNet → save badge.

**Body** (`multipart/form-data`):
```
image=<image file (JPG/PNG/WEBM, max 10MB)>
```

**Pipeline:**
1. PlantNet API identification (rejects < 30% confidence)
2. Sarvam AI fun fact generation
3. First-global-discovery check (40 pts bonus)
4. Save `PlantDiscovery` record (TEXT ONLY — image never stored)
5. Update `DailyStreak` + `UserTree`

**Response `200`:**
```json
{
  "common_name": "German Chamomile",
  "scientific_name": "Matricaria chamomilla",
  "family": "Asteraceae",
  "confidence": 0.94,
  "fun_fact": "Chamomile was used in ancient Egypt as a remedy for fevers...",
  "is_first_global": false,
  "points_earned": 10,
  "discovery_id": 3,
  "emoji": "🌻"
}
```

**Errors:**
- `422` — confidence < 30% ("Try a clearer photo!")
- `413` — image > 10MB

**Points:**
- First global discovery: **40 pts**
- New species for user: **10 pts**
- Re-discover same species: **5 pts**

---

### `POST /challenge/chat` 🔒
Chat about an identified plant using Sarvam AI.

**Body:**
```json
{ "message": "Is chamomile good for digestion?", "plant_name": "German Chamomile", "discovery_id": 3 }
```
**Response `200`:**
```json
{ "response": "Yes! Chamomile is well known for its gentle digestive support..." }
```

---

### `GET /challenge/streak` 🔒
Get 7-day streak data (today + 6 prior days).

**Response `200`:**
```json
{
  "days": [
    { "date": "2026-02-20", "verified": true, "plant_count": 2 },
    { "date": "2026-02-21", "verified": false, "plant_count": 0 }
  ],
  "current_streak": 3,
  "total_days": 12
}
```

---

### `GET /challenge/streak/mini` 🔒
Same as `/challenge/streak` — lightweight endpoint used by the dashboard widget.

---

### `GET /challenge/tree` 🔒
Get user's virtual growing tree state.

**Response `200`:**
```json
{ "total_leaves": 14, "total_points": 130, "tree_level": 3 }
```

Tree levels: every 5 plants = +1 level (max Level 10).

---

### `GET /challenge/badges` 🔒
Get all plant badges for current user (newest first).

**Response `200`:**
```json
[{
  "id": 3,
  "common_name": "German Chamomile",
  "scientific_name": "Matricaria chamomilla",
  "emoji": "🌻",
  "badge_color": "#40916C",
  "confidence": 0.94,
  "is_first_global": false,
  "points_earned": 10,
  "discovered_at": "2026-02-26T10:00:00",
  "fun_fact": "Chamomile was used in ancient Egypt..."
}]
```

---

## HTML Pages

| URL | Description |
|---|---|
| `GET /` | Landing page |
| `GET /login` | Login form |
| `GET /register` | Registration form |
| `GET /dashboard` | User dashboard with streak widget |
| `GET /profile/{id}` | Public profile |
| `GET /profile/edit` | Edit own profile |
| `GET /leaderboard` | Rankings |
| `GET /farmservice` | Farm management dashboard |
| `GET /aihelp` | AI chat + voice orb |
| `GET /challenge` | Plant discovery + growing tree |

---

## Error Reference

| Code | Meaning |
|---|---|
| `400` | Bad request (duplicate username/email, custom validation) |
| `401` | Missing or invalid JWT token |
| `403` | Valid token but resource belongs to another user |
| `404` | Resource not found |
| `413` | Uploaded file too large |
| `422` | Pydantic validation failure or low-confidence plant ID |
| `502` | External API failure (Sarvam STT/TTS, PlantNet) |
| `500` | Unexpected server error |
