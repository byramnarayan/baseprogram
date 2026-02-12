# Carbon Credit Farm Management System - Technical Documentation

A comprehensive, production-ready **FastAPI** application for carbon credit farm management with geospatial features, JWT authentication, and Neo4j graph database integration.

---

## 🎯 Project Overview

This system enables farmers to register their farms, calculate carbon credits based on soil type and area, and manage their farm portfolios through an authenticated web application. The system uses modern async Python with SQLAlchemy ORM for relational data and Neo4j for graph-based relationships.

### Core Features

- 🔐 **JWT-Based Authentication** - Secure token-based user authentication
- 🌾 **Farm Management** - CRUD operations for farms with geospatial data
- 📊 **Carbon Credit Calculation** - Dynamic calculation based on soil type, area, and verification status
- 🗺️ **Geospatial Support** - Polygon-based farm boundaries with area calculation
- 👥 **User Management** - Profile management with role-based access
- 📈 **Dashboard Analytics** - Aggregated statistics and leaderboard
- 🎨 **Modern Frontend** - Server-side rendered Jinja2 templates with interactive JavaScript

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Jinja2     │  │  JavaScript  │  │  TailwindCSS │      │
│  │  Templates   │  │   Modules    │  │    Styles    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    FastAPI   │  │   Routers    │  │     Auth     │      │
│  │   main.py    │  │  (Endpoints) │  │  Middleware  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                       Business Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Schemas    │  │   Utilities  │  │  Validators  │      │
│  │  (Pydantic)  │  │  (Calculators)│ │  (Business)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SQLAlchemy  │  │    Models    │  │   Database   │      │
│  │     ORM      │  │   (User,     │  │   Session    │      │
│  │              │  │    Farm)     │  │  Management  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                       Storage Layer                          │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   SQLite     │              │    Neo4j     │            │
│  │   (Primary)  │              │   (Graph)    │            │
│  └──────────────┘              └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - Async ORM with declarative models
- **Pydantic** - Data validation and settings management
- **JWT (python-jose)** - Token-based authentication
- **Passlib (bcrypt)** - Password hashing
- **Uvicorn** - ASGI server

**Database:**
- **SQLite** (Development) - File-based relational database
- **PostgreSQL** (Production-ready) - Scalable relational database
- **Neo4j Aura** - Graph database for relationship management

**Frontend:**
- **Jinja2** - Server-side templating engine
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript (ES6+)** - Client-side interactivity
- **Fetch API** - RESTful API communication

---

## 📁 Project Structure (Detailed)

```
baseprogram/
├── main.py                    # FastAPI app initialization & routing
├── database.py                # Database engine, session, ORM base
├── auth.py                    # JWT creation, verification, dependencies
├── config.py                  # Pydantic settings & environment config
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py           # Model exports
│   ├── user.py               # User table definition
│   └── farm.py               # Farm table with geospatial data
│
├── schemas/                   # Pydantic validation schemas
│   ├── __init__.py           # Schema exports
│   ├── auth.py               # Token schemas
│   ├── user.py               # UserCreate, UserUpdate, UserResponse
│   └── farm.py               # FarmCreate, FarmUpdate, FarmResponse
│
├── routers/                   # API endpoint modules
│   ├── __init__.py           # Router exports
│   ├── auth.py               # /api/auth/* - register, login, logout
│   ├── users.py              # /api/users/* - user CRUD
│   ├── leaderboard.py        # /api/leaderboard - rankings
│   └── farmservice.py        # /api/farmservice/* - farm CRUD
│
├── utils/                     # Utility modules
│   ├── __init__.py           # Utility exports
│   ├── carbon_calculator.py  # Carbon credit calculations
│   └── geospatial.py         # Area calculation, polygon center
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template with navbar
│   ├── home.html             # Landing page
│   ├── login.html            # Login form
│   ├── register.html         # Registration form
│   ├── dashboard.html        # User dashboard
│   ├── profile.html          # Public profile view
│   ├── profile_edit.html     # Profile editing
│   ├── leaderboard.html      # Rankings display
│   ├── farmservice.html      # Farm management dashboard
│   └── error.html            # Error page
│
├── static/                    # Static assets
│   ├── css/                  # Custom stylesheets
│   └── js/                   # JavaScript modules
│       ├── auth.js           # Token management
│       ├── utils.js          # Helper functions
│       └── farmservice.js    # Farm CRUD logic
│
├── media/                     # User uploads
│   └── profile_pics/         # Profile pictures
│
├── .env                       # Environment variables (SECRET_KEY, Neo4j)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🗄️ Database Architecture

### Database Schema (SQLite/PostgreSQL)

#### **Users Table**

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address TEXT,
    photo VARCHAR(255),
    password_hash VARCHAR(200) NOT NULL,
    points INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email_lower ON users (email);
CREATE INDEX idx_user_username_lower ON users (username);
```

**Key Features:**
- Auto-incrementing primary key
- Unique constraints on `username` and `email`
- Case-insensitive indexes for login
- Password stored as bcrypt hash (never plain text)
- Points system for gamification
- One-to-many relationship with farms

#### **Farms Table**

```sql
CREATE TABLE farms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    farmer_id INTEGER NOT NULL,
    farm_name VARCHAR(100),
    phone VARCHAR(15) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    area_hectares FLOAT NOT NULL,
    soil_type VARCHAR(20) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    annual_credits FLOAT DEFAULT 0.0,
    annual_value_inr FLOAT DEFAULT 0.0,
    polygon_coordinates JSON NOT NULL,
    is_verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (farmer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_farmer_verified ON farms (farmer_id, is_verified);
CREATE INDEX idx_location ON farms (latitude, longitude);
CREATE INDEX idx_district_state ON farms (district, state);
```

**Key Features:**
- Foreign key to `users` table with cascade delete
- Geospatial data: `latitude`, `longitude`, `polygon_coordinates` (JSON array)
- Calculated fields: `annual_credits`, `annual_value_inr` (denormalized for performance)
- Verification workflow support (`is_verified`)
- Composite indexes for common queries
- Auto-updating `updated_at` timestamp

### Database Models (SQLAlchemy)

**User Model** (`models/user.py`):
```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    # ... other fields
    
    # Relationship
    farms: Mapped[list["Farm"]] = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
```

**Farm Model** (`models/farm.py`):
```python
class Farm(Base):
    __tablename__ = "farms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    polygon_coordinates: Mapped[List] = mapped_column(JSON)
    # ... other fields
    
    # Relationship
    owner: Mapped["User"] = relationship("User", back_populates="farms")
```

### Neo4j Graph Database

**Connection Configuration** (`config.py`):
```python
neo4j_uri: str          # Neo4j Aura instance URI
neo4j_username: str     # Database username
neo4j_password: str     # Database password
neo4j_database: str     # Database name
aura_instanceid: str    # Aura instance ID
```

**Use Cases:**
- User-farm relationships
- Farm proximity graphs
- Social network features (future)
- Recommendation systems (future)

---

## 🔐 Authentication System

### JWT Token Flow

```
1. User Registration/Login
   ↓
2. Server generates JWT token
   - Payload: {"sub": "user_id", "exp": timestamp}
   - Signed with SECRET_KEY using HS256
   ↓
3. Client stores token (localStorage)
   ↓
4. Client includes token in Authorization header
   - Header: "Authorization: Bearer <token>"
   ↓
5. Server validates token via get_current_user dependency
   - Verifies signature
   - Checks expiration
   - Fetches user from database
   ↓
6. User object injected into protected routes
```

### Implementation Details

**Password Hashing** (`auth.py`):
```python
# Hash password on registration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(plain_password)

# Verify password on login
is_valid = pwd_context.verify(plain_password, hashed_password)
```

**Token Creation** (`auth.py`):
```python
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return jwt_token
```

**Token Validation** (`auth.py`):
```python
async def get_current_user(token: str, db: AsyncSession):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    user = await db.execute(select(User).where(User.id == int(user_id)))
    return user.scalar_one_or_none()
```

### Protected Routes

All routes with `current_user: User = Depends(get_current_user)` require authentication:
- `GET /api/users/me` - Get current user
- `PATCH /api/users/me` - Update profile
- `DELETE /api/users/me` - Delete account
- `GET /api/farmservice/farms` - List farms
- `POST /api/farmservice/farms` - Create farm
- And more...

---

## 🌐 API Architecture

### RESTful API Design

The API follows REST conventions with clear resource-based URLs and HTTP methods:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| **Authentication** |
| POST | `/api/auth/register` | Create new user | ❌ |
| POST | `/api/auth/token` | Login (get JWT) | ❌ |
| POST | `/api/auth/logout` | Logout | ❌ |
| **Users** |
| GET | `/api/users/me` | Get current user | ✅ |
| PATCH | `/api/users/me` | Update current user | ✅ |
| DELETE | `/api/users/me` | Delete account | ✅ |
| GET | `/api/users/{user_id}` | Get public profile | ❌ |
| **Farms** |
| GET | `/api/farmservice/farms` | List user's farms | ✅ |
| POST | `/api/farmservice/farms` | Create new farm | ✅ |
| GET | `/api/farmservice/farms/{farm_id}` | Get farm details | ✅ |
| PUT | `/api/farmservice/farms/{farm_id}` | Update farm | ✅ |
| DELETE | `/api/farmservice/farms/{farm_id}` | Delete farm | ✅ |
| GET | `/api/farmservice/statistics` | Get statistics | ✅ |
| **Leaderboard** |
| GET | `/api/leaderboard` | Get user rankings | ❌ |

### API Request/Response Flow

**Example: Create Farm**

```http
POST /api/farmservice/farms
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "farm_name": "Green Valley Farm",
  "phone": "9876543210",
  "district": "Pune",
  "state": "Maharashtra",
  "soil_type": "Loamy",
  "polygon_coordinates": [
    [18.5204, 73.8567],
    [18.5214, 73.8567],
    [18.5214, 73.8577],
    [18.5204, 73.8577]
  ]
}
```

**Backend Processing:**
1. **Authentication**: `get_current_user` dependency validates JWT token
2. **Validation**: Pydantic `FarmCreate` schema validates input
3. **Geospatial Calculation**: 
   - `calculate_area_from_polygon()` computes area in hectares
   - `get_polygon_center()` finds center coordinates
4. **Carbon Credit Calculation**:
   - `calculate_annual_credits(area, soil_type, is_verified=False)`
   - `calculate_annual_value(credits)` converts to INR
5. **Database Storage**: SQLAlchemy creates Farm record
6. **Response**: Returns serialized `FarmResponse`

```json
{
  "id": 1,
  "farmer_id": 123,
  "farm_name": "Green Valley Farm",
  "phone": "9876543210",
  "latitude": 18.5209,
  "longitude": 73.8572,
  "area_hectares": 0.012,
  "soil_type": "Loamy",
  "district": "Pune",
  "state": "Maharashtra",
  "annual_credits": 0.09,
  "annual_value_inr": 45.0,
  "polygon_coordinates": [...],
  "is_verified": false,
  "created_at": "2026-02-12T13:30:00",
  "updated_at": "2026-02-12T13:30:00",
  "display_name": "Green Valley Farm",
  "verification_status": "Pending Verification"
}
```

### Validation & Error Handling

**Pydantic Validation** (`schemas/farm.py`):
```python
class FarmCreate(BaseModel):
    soil_type: Literal["Loamy", "Clay", "Sandy", "Mixed"]  # Enum constraint
    polygon_coordinates: List[List[float]]  # Type safety
    
    @field_validator("polygon_coordinates")
    def validate_polygon(cls, v):
        if len(v) < 3:
            raise ValueError("Polygon must have at least 3 points")
        for lat, lon in v:
            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude: {lat}")
        return v
```

**Error Responses**:
- `400 Bad Request` - Invalid input (custom validation)
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Valid token but insufficient permissions
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Pydantic validation failure
- `500 Internal Server Error` - Unexpected server error

---

## ⚙️ Business Logic & Utilities

### Carbon Credit Calculator

**Formula** (`utils/carbon_calculator.py`):
```python
annual_credits = area_hectares × soil_multiplier × base_rate × verification_multiplier

Where:
- base_rate = 12.5 credits/hectare/year
- soil_multiplier = {Loamy: 1.2, Clay: 1.0, Sandy: 0.8, Mixed: 1.0}
- verification_multiplier = {verified: 1.0, unverified: 0.5}

annual_value_inr = annual_credits × market_rate (₹500/credit)
```

**Example Calculation**:
```python
# Farm: 3.2 hectares, Loamy soil, Verified
area = 3.2
soil_type = "Loamy"  # multiplier = 1.2
is_verified = True   # multiplier = 1.0

credits = 3.2 × 1.2 × 12.5 × 1.0 = 48.0 credits/year
value = 48.0 × 500 = ₹24,000/year
```

### Geospatial Utilities

**Area Calculation** (`utils/geospatial.py`):
```python
def calculate_area_from_polygon(coordinates: List[List[float]]) -> float:
    """
    Calculate area using Haversine formula for geographic coordinates.
    Returns area in hectares.
    """
    # Uses spherical geometry to account for Earth's curvature
    # Converts polygon to projected coordinates
    # Calculates area using shoelace formula
    # Returns result in hectares
```

**Center Point** (`utils/geospatial.py`):
```python
def get_polygon_center(coordinates: List[List[float]]) -> tuple[float, float]:
    """
    Calculate centroid (geometric center) of polygon.
    Returns (latitude, longitude).
    """
    # Averages all coordinate points
    # Returns center for map display
```

---

## 🎨 Frontend Integration

### Server-Side Rendering (Jinja2)

**Base Template** (`templates/base.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }} - Farm Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <!-- Navigation bar with auth state -->
    <nav id="navbar">...</nav>
    
    <!-- Content block (overridden by child templates) -->
    {% block content %}{% endblock %}
    
    <!-- JavaScript modules -->
    <script src="/static/js/auth.js"></script>
    <script src="/static/js/utils.js"></script>
</body>
</html>
```

**Child Template** (`templates/farmservice.html`):
```html
{% extends "base.html" %}

{% block content %}
<div id="farm-dashboard">
    <h1>My Farms</h1>
    <div id="statistics"></div>
    <div id="farm-list"></div>
</div>

<script src="/static/js/farmservice.js"></script>
<script>
    // Fetch farms on page load
    document.addEventListener('DOMContentLoaded', async () => {
        await loadFarms();
    });
</script>
{% endblock %}
```

### Client-Side JavaScript

**Authentication Module** (`static/js/auth.js`):
```javascript
// Store/retrieve JWT token
function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

// Make authenticated API request
async function apiRequest(url, options = {}) {
    const token = getToken();
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    const response = await fetch(url, options);
    if (response.status === 401) {
        // Token expired, redirect to login
        window.location.href = '/login';
    }
    return response;
}
```

**Farm Service Module** (`static/js/farmservice.js`):
```javascript
// Fetch all farms with statistics
async function loadFarms() {
    const response = await apiRequest('/api/farmservice/farms');
    const data = await response.json();
    
    displayStatistics(data.summary);
    displayFarms(data.farms);
}

// Create new farm
async function createFarm(farmData) {
    const response = await apiRequest('/api/farmservice/farms', {
        method: 'POST',
        body: JSON.stringify(farmData)
    });
    
    if (response.ok) {
        const farm = await response.json();
        showNotification('Farm created successfully!');
        await loadFarms(); // Refresh list
    } else {
        const error = await response.json();
        showError(error.detail);
    }
}

// Delete farm
async function deleteFarm(farmId) {
    const response = await apiRequest(`/api/farmservice/farms/${farmId}`, {
        method: 'DELETE'
    });
    
    if (response.ok) {
        showNotification('Farm deleted successfully!');
        await loadFarms(); // Refresh list
    }
}
```

### Frontend-Backend Data Flow

```
1. User interactions (clicks, form submissions)
   ↓
2. JavaScript event handlers
   ↓
3. API requests with JWT token
   ↓
4. FastAPI routes validate & process
   ↓
5. Database operations (SQLAlchemy)
   ↓
6. Pydantic serialization
   ↓
7. JSON response to frontend
   ↓
8. JavaScript updates DOM dynamically
```

**Example Flow: Load Dashboard**
```
User opens /farmservice
  ↓
FastAPI serves farmservice.html (Jinja2)
  ↓
Browser loads farmservice.js
  ↓
JavaScript calls GET /api/farmservice/farms
  ↓
FastAPI validates JWT token
  ↓
SQLAlchemy queries farms table
  ↓
Calculates summary statistics
  ↓
Returns FarmListResponse JSON
  ↓
JavaScript renders farms in DOM
```

---

## 🚀 Running the Application

### Prerequisites

- Python 3.11+
- pip or uv package manager
- Neo4j Aura account (for graph features)

### Installation

1. **Clone Repository**
   ```bash
   cd baseprogram
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   
   Create `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here-generate-with-secrets.token_hex(32)
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # Neo4j Configuration
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   NEO4J_DATABASE=neo4j
   AURA_INSTANCEID=your-instance-id
   AURA_INSTANCENAME=your-instance-name
   ```

5. **Initialize Database**
   ```bash
   python main.py  # Creates SQLite database on first run
   ```

6. **Run Application**
   ```bash
   # Development mode
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   
   # Or using main.py
   python main.py
   ```

7. **Access Application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

---

## 🧪 API Testing

### Interactive Documentation

FastAPI auto-generates interactive API documentation:

1. **Swagger UI** (`/docs`):
   - Test endpoints directly in browser
   - View request/response schemas
   - Authenticate with JWT token

2. **ReDoc** (`/redoc`):
   - Beautiful, readable documentation
   - Search functionality
   - Code examples

### Manual Testing with cURL

**1. Register User**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Farmer",
    "username": "johnfarmer",
    "email": "john@farm.com",
    "phone": "9876543210",
    "password": "SecurePass123"
  }'
```

**2. Login**
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@farm.com&password=SecurePass123"
```

**3. Create Farm**
```bash
curl -X POST "http://localhost:8000/api/farmservice/farms" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "farm_name": "Sunrise Acres",
    "phone": "9876543210",
    "district": "Pune",
    "state": "Maharashtra",
    "soil_type": "Loamy",
    "polygon_coordinates": [
      [18.5204, 73.8567],
      [18.5214, 73.8567],
      [18.5214, 73.8577],
      [18.5204, 73.8577]
    ]
  }'
```

**4. Get Farms**
```bash
curl -X GET "http://localhost:8000/api/farmservice/farms" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 📊 Database Migrations

### SQLite to PostgreSQL Migration

For production deployment, migrate from SQLite to PostgreSQL:

1. **Update `database.py`**:
   ```python
   SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
   ```

2. **Install PostgreSQL Dependencies**:
   ```bash
   pip install asyncpg
   ```

3. **Run Migration Script**:
   ```bash
   python migrate_pure_schema.py
   ```

### Schema Updates

To add new fields or tables:

1. **Update Models** (`models/user.py` or `models/farm.py`)
2. **Drop Existing Tables** (development only):
   ```python
   await Base.metadata.drop_all(engine)
   ```
3. **Recreate Tables**:
   ```python
   await Base.metadata.create_all(engine)
   ```

For production, use Alembic migrations.

---

## 🔒 Security Best Practices

### Implemented Security Measures

1. **Password Security**
   - Bcrypt hashing with salt
   - Never store plain text passwords
   - Minimum 8 character length enforced

2. **JWT Token Security**
   - Secret key stored in environment variables
   - Expiration time (60 minutes default)
   - Signed with HS256 algorithm

3. **Input Validation**
   - Pydantic schemas validate all inputs
   - SQL injection prevention (SQLAlchemy ORM)
   - XSS protection (Jinja2 auto-escaping)

4. **Authorization**
   - Route-level authentication checks
   - Ownership verification (users can only modify their farms)
   - Public/private data separation

5. **Database Security**
   - Foreign key constraints
   - Cascade deletes
   - Prepared statements (ORM)

### Production Recommendations

1. **Use HTTPS** - Encrypt all traffic
2. **Rotate Secret Keys** - Periodic key rotation
3. **Rate Limiting** - Prevent brute force attacks
4. **CORS Configuration** - Restrict allowed origins
5. **Database Backups** - Regular automated backups
6. **Logging & Monitoring** - Track security events

---

## 📈 Performance Optimization

### Backend Optimizations

1. **Async/Await** - Non-blocking I/O operations
2. **Connection Pooling** - SQLAlchemy connection pool
3. **Indexing** - Database indexes on frequently queried columns
4. **Denormalization** - Calculated fields stored in database
5. **Lazy Loading** - Minimal data fetched by default

### Frontend Optimizations

1. **Static File Caching** - Browser caching for CSS/JS
2. **CDN Hosting** - Serve static assets from CDN
3. **Minimal API Calls** - Batch requests where possible
4. **DOM Manipulation** - Efficient JavaScript updates

### Scaling Strategies

1. **Horizontal Scaling** - Multiple Uvicorn workers
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Caching** - Redis for session storage, API responses
3. **Load Balancing** - Nginx reverse proxy
4. **Database Optimization** - PostgreSQL with read replicas

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Locked Error (SQLite)**
- **Cause**: Concurrent write operations
- **Solution**: Use PostgreSQL for production

**2. Token Expired / 401 Unauthorized**
- **Cause**: JWT token expired
- **Solution**: Re-login to get new token

**3. CORS Errors**
- **Cause**: Frontend on different origin
- **Solution**: Configure CORS middleware in `main.py`

**4. Module Not Found**
- **Cause**: Dependencies not installed
- **Solution**: `pip install -r requirements.txt`

**5. Port Already in Use**
- **Cause**: Another process using port 8000
- **Solution**: Change port or kill existing process
  ```bash
  # Windows
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8000 | xargs kill
  ```

---

## 📚 Additional Resources

- **API Documentation**: [`API_DOCS.md`](./API_DOCS.md)
- **Learning Guide**: [`LEARNING.md`](./LEARNING.md)
- **System Design**: [`CARBON_CREDIT_SYSTEM_DESIGN.md`](./CARBON_CREDIT_SYSTEM_DESIGN.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org
- **Pydantic Docs**: https://docs.pydantic.dev

---

## 📞 Support & Contributing

For questions, issues, or contributions:
1. Review inline code comments (comprehensive documentation)
2. Check existing documentation files
3. Test endpoints using `/docs` interface
4. Consult official framework documentation

---

**Built with ❤️ for modern carbon credit management**
