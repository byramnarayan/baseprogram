# FastAPI User Management Application - AI Agent Build Prompt

## Project Overview
Build a complete FastAPI application with SQLite database (upgradable), Jinja2 templates, and Tailwind CSS styling. The app is a user management system with authentication, authorization, profile management, and a points-based leaderboard.

---

## Core Requirements

### 1. User Database Schema
Create a User model with these fields:
- `id` (primary key, auto-increment)
- `name` (string, max 100 chars)
- `username` (string, unique, max 50 chars)
- `email` (string, unique, max 120 chars)
- `phone` (string, max 15 chars)
- `address` (text, nullable)
- `photo` (string, nullable - stores filename)
- `password_hash` (string, 200 chars)
- `points` (integer, default 0)
- `created_at` (datetime, auto-set)

Include a `image_path` property that returns:
- `/media/profile_pics/{photo}` if photo exists
- `/static/profile_pics/default.jpg` otherwise

---

## 2. Project Structure (Modular)

```
project/
├── routers/
│   ├── __init__.py
│   ├── auth.py          # Login, Register, Logout endpoints
│   ├── users.py         # User CRUD, Profile operations
│   └── leaderboard.py   # Leaderboard endpoints
├── models/
│   ├── __init__.py
│   └── user.py          # User model
├── schemas/
│   ├── __init__.py
│   ├── user.py          # User schemas (Create, Update, Response)
│   └── auth.py          # Token schema
├── templates/
│   ├── base.html        # Base layout with navbar
│   ├── login.html       # Login page (Tailwind modal)
│   ├── register.html    # Register page (Tailwind modal)
│   ├── dashboard.html   # User dashboard (profile card)
│   ├── profile_edit.html # Edit profile + delete account
│   ├── profile.html     # View other user's profile
│   ├── leaderboard.html # Points leaderboard
│   └── error.html       # Error page
├── static/
│   ├── css/
│   │   └── custom.css   # Additional styles if needed
│   ├── js/
│   │   ├── auth.js      # Auth utilities (getCurrentUser, logout, etc.)
│   │   └── utils.js     # Helper functions
│   └── profile_pics/
│       └── default.jpg  # Default profile picture
├── media/
│   └── profile_pics/    # Uploaded user photos
├── database.py          # Database connection & session
├── auth.py              # Auth functions (hash, verify, create_token, get_current_user)
├── config.py            # Settings (SECRET_KEY, TOKEN_EXPIRE, etc.)
├── main.py              # FastAPI app, route templates, lifespan
└── .env                 # Environment variables
```

---

## 3. Authentication & Authorization

### Auth Functions (auth.py)
- `hash_password(password: str) -> str` - Use pwdlib
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(data: dict, expires_delta: timedelta) -> str` - JWT token
- `verify_access_token(token: str) -> str | None` - Returns user_id if valid
- `get_current_user(token, db) -> User` - Dependency for protected routes
- `CurrentUser = Annotated[User, Depends(get_current_user)]`

### OAuth2 Setup
```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")
```

### Protected Routes
Any route requiring authentication should use `current_user: CurrentUser` dependency.

---

## 4. API Endpoints (REST)

### Auth Routes (`/api/auth`)
- `POST /api/auth/register` - Create new user
  - Body: `{name, username, email, phone, address?, password}`
  - Returns: `UserPrivate` (includes email)
  - Validates: unique username, unique email, password min 8 chars
  
- `POST /api/auth/token` - Login
  - Body: `OAuth2PasswordRequestForm` (username=email, password)
  - Returns: `{access_token, token_type}`
  - Auth: Email + password (case-insensitive email)
  
- `POST /api/auth/logout` - Logout (frontend clears token)

### User Routes (`/api/users`)
- `GET /api/users/me` - Get current user (protected)
  - Returns: `UserPrivate`
  
- `PATCH /api/users/me` - Update current user (protected)
  - Body: `{name?, username?, photo?}`
  - Returns: `UserPrivate`
  - Validates: unique username if changed
  
- `DELETE /api/users/me` - Delete current user (protected)
  - Returns: 204 No Content
  
- `GET /api/users/{user_id}` - View any user profile (public)
  - Returns: `UserPublic` (no email)

### Leaderboard Routes (`/api/leaderboard`)
- `GET /api/leaderboard` - Get users ordered by points DESC
  - Returns: `list[UserPublic]`
  - Optional query params: `limit` (default 100)

---

## 5. Pydantic Schemas

### User Schemas (schemas/user.py)
```python
class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=15)
    address: str | None = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: str
    photo: str | None
    image_path: str
    points: int

class UserPrivate(UserPublic):
    email: EmailStr
    phone: str
    address: str | None

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    username: str | None = Field(default=None, min_length=1, max_length=50)
    photo: str | None = None
```

### Auth Schemas (schemas/auth.py)
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

---

## 6. Frontend Routes (HTML Pages)

All routes in `main.py`:

- `GET /` - Redirect to `/dashboard` if logged in, else `/login`
- `GET /login` - Login page (Tailwind modal form)
- `GET /register` - Register page (Tailwind modal form)
- `GET /dashboard` - User's own profile card (protected)
- `GET /profile_edit` - Edit profile + delete account (protected)
- `GET /leaderboard` - Leaderboard table
- `GET /profile/{user_id}` - View other user's profile (public)

---

## 7. UI Design System (Tailwind CSS)

### Typography
```css
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Apply globally */
font-family: 'Inter', sans-serif;

/* Headings */
font-weight: 700;
letter-spacing: -0.01em;

/* Buttons */
font-weight: 600;
letter-spacing: 0.02em;
```

### Color Classes (Custom Tailwind Config)
Add to `tailwind.config.js` or use arbitrary values:

**Primary Palette:**
- Primary Brand: `bg-[#31694E]` / `text-[#31694E]`
- Primary Action: `bg-[#658C58]` / `text-[#658C58]`
- Secondary Accent: `bg-[#BBC863]` / `text-[#BBC863]`
- Soft Accent: `bg-[#F0E491]` / `text-[#F0E491]`

**Neutral:**
- White: `bg-white`
- Page BG: `bg-[#F9FAFB]`
- Secondary Text: `text-[#6B7280]`
- Primary Text: `text-[#111827]`

**States:**
- Success: `bg-[#658C58]`
- Warning: `bg-[#F0E491]`
- Error: `bg-[#E74C3C]`
- Info: `bg-[#3B82F6]`

### Component Styles

**Buttons:**
```html
<button class="bg-[#658C58] hover:bg-[#31694E] text-white font-semibold 
               rounded-xl px-6 py-3 transition-all duration-200 
               tracking-wide">
  Button Text
</button>
```

**Cards:**
```html
<div class="bg-white rounded-xl shadow-lg hover:shadow-xl 
            transition-shadow duration-200 p-6">
  Card Content
</div>
```

**Inputs:**
```html
<input class="w-full px-4 py-3 rounded-lg border border-[#D1D5DB] 
              focus:border-[#658C58] focus:ring-2 focus:ring-[#658C58]/40 
              focus:outline-none transition-all duration-200"
       type="text">
```

**Spacing:** Use 8-based scale
- `p-1.5` (6px), `p-3` (12px), `p-4.5` (18px), `p-6` (24px), `p-7.5` (30px), etc.

---

## 8. JavaScript Frontend (auth.js)

```javascript
let currentUser = null;
let fetchPromise = null;

export async function getCurrentUser() {
  if (currentUser) return currentUser;
  if (fetchPromise) return fetchPromise;
  
  const token = localStorage.getItem("access_token");
  if (!token) return null;
  
  fetchPromise = (async () => {
    try {
      const response = await fetch("/api/users/me", {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        currentUser = await response.json();
        return currentUser;
      }
      localStorage.removeItem("access_token");
      return null;
    } catch (error) {
      console.error("Error fetching user:", error);
      return null;
    } finally {
      fetchPromise = null;
    }
  })();
  
  return fetchPromise;
}

export function logout() {
  localStorage.removeItem("access_token");
  currentUser = null;
  window.location.href = "/login";
}

export function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  localStorage.setItem("access_token", token);
}

export function clearUserCache() {
  currentUser = null;
}
```

---

## 9. Key Implementation Details

### Login Flow
1. User submits email + password via form
2. Frontend calls `POST /api/auth/token` with `OAuth2PasswordRequestForm`
3. Backend validates credentials, returns JWT token
4. Frontend stores token in `localStorage` as `access_token`
5. Redirect to `/dashboard`

### Register Flow
1. User submits registration form
2. Frontend calls `POST /api/auth/register`
3. Backend creates user with hashed password
4. Auto-login: call `/api/auth/token` and store token
5. Redirect to `/dashboard`

### Protected Pages
All protected HTML pages should:
```javascript
async function checkAuth() {
  const user = await getCurrentUser();
  if (!user) {
    window.location.href = '/login';
    return;
  }
  // Load page content
}
checkAuth();
```

### Authorization (Profile Edit/Delete)
- Only the logged-in user can edit/delete their own profile
- Backend checks: `if user_id != current_user.id: raise 403 Forbidden`
- Frontend hides edit/delete buttons for other users' profiles

### File Upload (Profile Photo)
- Use `<input type="file" accept="image/*">`
- Upload to `/media/profile_pics/`
- Save filename in database `photo` field
- Return full path via `image_path` property

---

## 10. Database Setup (database.py)

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 11. Configuration (config.py)

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
```

**.env file:**
```
SECRET_KEY=your-secret-key-here-change-in-production
```

---

## 12. Main App (main.py)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import Base, engine
from routers import auth, users, leaderboard

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# Templates
templates = Jinja2Templates(directory="templates")

# API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])

# HTML Routes
@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request, "base.html", {"title": "Home"})

# Add other template routes (login, register, dashboard, etc.)
```

---

## 13. Template Structure

### base.html
- Include CDN for Tailwind CSS and Inter font
- Navbar with logo, login/register (logged out) or dashboard/logout (logged in)
- Use `{% block content %}{% endblock %}` for page content
- Include `auth.js` script to update navbar based on auth state

### login.html / register.html
- Use Tailwind modal/card design
- Center-aligned form on page background `bg-[#F9FAFB]`
- Form fields styled per design system
- Submit via JavaScript fetch to API
- Display error messages in red alert box

### dashboard.html
- Profile card with:
  - Photo (circular, 120px)
  - Name, username, email, phone
  - Address (if exists)
  - Points badge
  - "Edit Profile" button → `/profile_edit`

### profile_edit.html
- Form to update name, username, photo
- "Delete Account" button (danger zone, requires confirmation modal)
- Only accessible to logged-in user for their own profile

### leaderboard.html
- Table or card grid showing all users
- Columns: Rank, Photo, Name, Username, Points
- Sorted by points DESC
- Click name → `/profile/{user_id}`

### profile.html
- View-only profile card
- No edit/delete options (unless viewing own profile → redirect to dashboard)

---

## 14. Error Handling

- 401 Unauthorized → Redirect to `/login`
- 403 Forbidden → Show error message "You are not authorized"
- 404 Not Found → Show error page
- 422 Validation Error → Show error message with field details
- 500 Server Error → Generic error page

---

## 15. Additional Features (Future-Ready)

The modular structure allows adding:
- Password reset (email token)
- Email verification
- Admin panel
- Activity logging
- Points system (add/subtract points)
- Social features (friends, messaging)
- File upload for documents
- API versioning

---

## 16. Development Checklist

### Backend
- [ ] Set up database.py with async SQLite
- [ ] Create User model with all fields
- [ ] Implement auth.py (hash, verify, tokens, get_current_user)
- [ ] Create config.py with settings
- [ ] Build auth router (register, login)
- [ ] Build users router (me, update, delete, get user)
- [ ] Build leaderboard router (get all by points)
- [ ] Create all Pydantic schemas
- [ ] Set up main.py with lifespan, routers, static/media
- [ ] Test all API endpoints

### Frontend
- [ ] Create base.html with navbar and Tailwind CDN
- [ ] Build auth.js with getCurrentUser, logout, etc.
- [ ] Create login.html with form and API integration
- [ ] Create register.html with form and API integration
- [ ] Create dashboard.html with profile card
- [ ] Create profile_edit.html with update/delete
- [ ] Create leaderboard.html with points table
- [ ] Create profile.html for viewing others
- [ ] Add error.html for error handling
- [ ] Style all pages per design system
- [ ] Test authentication flow end-to-end

### File Structure
- [ ] Create routers/, models/, schemas/ as packages with __init__.py
- [ ] Create static/css/, static/js/, static/profile_pics/
- [ ] Create media/profile_pics/
- [ ] Add default.jpg to static/profile_pics/
- [ ] Create .env file with SECRET_KEY

---

## 17. Testing Guide

1. **Register a new user** → Should create account and auto-login
2. **Login with email + password** → Should redirect to dashboard
3. **View dashboard** → Should show current user's profile card
4. **Edit profile** → Update name/username → Should reflect changes
5. **View leaderboard** → Should show all users sorted by points
6. **Click another user's name** → Should show their profile (view-only)
7. **Try to edit another user** → Should get 403 Forbidden
8. **Delete account** → Should remove user and all data, redirect to home
9. **Logout** → Should clear token and redirect to login

---

## 18. Code Quality Requirements

- Use **async/await** for all database operations
- Use **type hints** throughout (Python 3.11+)
- Follow **PEP 8** style guide
- Add **docstrings** to all functions
- Use **dependency injection** for database sessions
- Implement **proper error handling** (try/except, HTTPException)
- Validate **all user inputs** with Pydantic
- Use **case-insensitive** email/username lookups
- **Hash passwords** before storing (never store plain text)
- **Sanitize file uploads** (check extension, size, rename)

---

## 19. Security Best Practices

- Store passwords with pwdlib (bcrypt/argon2)
- Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
- Set token expiration (60 minutes)
- Validate JWT tokens on every protected route
- Check user ownership before update/delete
- Sanitize file uploads (extension whitelist, size limit)
- Use HTTPS in production
- Add CORS middleware if needed
- Rate limit login attempts (future)
- Log security events (future)

---

## 20. Deployment Prep (Future)

- Use PostgreSQL instead of SQLite
- Set up Alembic for migrations
- Use environment variables for all secrets
- Deploy to cloud (Render, Railway, AWS, etc.)
- Set up CI/CD pipeline
- Add monitoring and logging
- Configure HTTPS/SSL
- Set up CDN for static files
- Add database backups
- Use Redis for caching

---

## Final Notes

This specification provides everything needed to build a production-ready FastAPI application with:
- ✅ Full authentication (JWT tokens)
- ✅ Authorization (user ownership checks)
- ✅ RESTful API design
- ✅ Modern UI (Tailwind + design system)
- ✅ Modular structure (scalable)
- ✅ Security best practices
- ✅ Async database operations
- ✅ File uploads
- ✅ Error handling

**Build this app step-by-step, test each feature thoroughly, and ensure all routes work before moving to the next section.**
