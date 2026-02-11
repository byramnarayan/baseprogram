# FastAPI Learning Guide for Interns

Welcome! This guide will help you understand the FastAPI User Management project and learn modern web development concepts.

## 📚 Table of Contents

1. [Understanding the Architecture](#understanding-the-architecture)
2. [FastAPI Fundamentals](#fastapi-fundamentals)
3. [Database with SQLAlchemy](#database-with-sqlalchemy)
4. [Authentication & Security](#authentication--security)
5. [Frontend Integration](#frontend-integration)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Exercises](#exercises)

---

## Understanding the Architecture

### The Big Picture

```
User Browser
     ↓
HTML/JavaScript (Frontend)
     ↓
FastAPI Routes (Backend)
     ↓
Business Logic (Auth, Validation)
     ↓
Database (SQLite/PostgreSQL)
```

### Request Flow Example

1. **User clicks "Login"** → JavaScript sends POST request
2. **FastAPI receives request** → Validates credentials
3. **Database query** → Checks if user exists
4. **Response** → Returns JWT token
5. **Frontend stores token** → Used for future requests

---

## FastAPI Fundamentals

### What is FastAPI?

FastAPI is a modern Python web framework that:
- ✅ Automatically validates request data
- ✅ Generates interactive API documentation
- ✅ Supports async/await for better performance
- ✅ Uses Python type hints for clarity

### Basic Route Example

```python
@app.get("/hello")
async def hello_world():
    return {"message": "Hello, World!"}
```

**Key Points:**
- `@app.get()` - Decorator that defines a GET endpoint
- `async def` - Asynchronous function (non-blocking)
- Return value - Automatically converted to JSON

### Path Parameters

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # user_id is automatically converted to int
    return {"user_id": user_id}
```

### Query Parameters

```python
@app.get("/search")
async def search(q: str, limit: int = 10):
    # q is required, limit is optional (default 10)
    return {"query": q, "limit": limit}
```

### Request Body with Pydantic

```python
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    
@app.post("/users")
async def create_user(user: UserCreate):
    # user is automatically validated
    return user
```

---

## Database with SQLAlchemy

### What is an ORM?

ORM (Object-Relational Mapping) lets you work with databases using Python objects instead of SQL.

**Without ORM (Raw SQL):**
```sql
SELECT * FROM users WHERE id = 1;
```

**With ORM (SQLAlchemy):**
```python
user = await db.execute(select(User).where(User.id == 1))
```

### Defining Models

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
```

**Key Concepts:**
- `Base` - All models inherit from this
- `__tablename__` - Name of the database table
- `Mapped[type]` - Type annotation for SQLAlchemy 2.0
- `mapped_column()` - Defines column properties

### Common Database Operations

**Create:**
```python
new_user = User(name="John", email="john@example.com")
db.add(new_user)
await db.commit()
await db.refresh(new_user)  # Get auto-generated ID
```

**Read:**
```python
# Get one user
result = await db.execute(select(User).where(User.id == 1))
user = result.scalar_one_or_none()

# Get all users
result = await db.execute(select(User))
users = result.scalars().all()
```

**Update:**
```python
user.name = "Jane"
await db.commit()
await db.refresh(user)
```

**Delete:**
```python
await db.delete(user)
await db.commit()
```

---

## Authentication & Security

### Password Hashing

**❌ NEVER DO THIS:**
```python
user.password = "mypassword123"  # Plain text!
```

**✅ ALWAYS DO THIS:**
```python
from auth import hash_password
user.password_hash = hash_password("mypassword123")
```

**Why?**
- If database is compromised, passwords are still safe
- Hashing is one-way (can't reverse it)
- We use Argon2 (industry-standard algorithm)

### JWT Tokens

**What is JWT?**
- JSON Web Token - a way to securely transmit information
- Contains user data (claims) and a signature
- Stateless - server doesn't need to store sessions

**Structure:**
```
header.payload.signature
eyJhbGci...  .  eyJzdWIi...  .  SflKxwRJ...
```

**Creating a Token:**
```python
token = create_access_token(data={"sub": str(user.id)})
# Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Using a Token:**
```python
# Client sends in Authorization header:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Protected Routes

```python
@app.get("/protected")
async def protected_route(current_user: CurrentUser):
    # This route requires authentication
    # current_user is automatically injected
    return {"user": current_user.username}
```

**How it works:**
1. Client sends token in Authorization header
2. `get_current_user` dependency verifies token
3. If valid, user object is injected into route
4. If invalid, 401 Unauthorized is returned

---

## Frontend Integration

### JavaScript Modules

**Why modules?**
- Organize code into reusable pieces
- Avoid global namespace pollution
- Import only what you need

**Exporting:**
```javascript
// auth.js
export function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
}
```

**Importing:**
```javascript
// In HTML
<script type="module">
    import { logout } from '/static/js/auth.js';
    document.getElementById('logout-btn').addEventListener('click', logout);
</script>
```

### Fetch API

**Making API Requests:**
```javascript
// GET request
const response = await fetch('/api/users/me', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const user = await response.json();

// POST request
const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: "John",
        email: "john@example.com",
        password: "SecurePass123"
    })
});
```

### LocalStorage

**Storing Data:**
```javascript
localStorage.setItem("access_token", token);
```

**Retrieving Data:**
```javascript
const token = localStorage.getItem("access_token");
```

**Removing Data:**
```javascript
localStorage.removeItem("access_token");
```

---

## Best Practices

### 1. Always Use Type Hints

**❌ Bad:**
```python
def get_user(user_id):
    return user
```

**✅ Good:**
```python
async def get_user(user_id: int) -> User | None:
    return user
```

### 2. Use Pydantic for Validation

**❌ Bad:**
```python
@app.post("/users")
async def create_user(request: Request):
    data = await request.json()
    # Manual validation...
```

**✅ Good:**
```python
@app.post("/users")
async def create_user(user: UserCreate):
    # Automatically validated!
```

### 3. Handle Errors Properly

**❌ Bad:**
```python
user = db.query(User).filter(User.id == user_id).first()
return user  # Returns None if not found (confusing!)
```

**✅ Good:**
```python
user = db.query(User).filter(User.id == user_id).first()
if not user:
    raise HTTPException(status_code=404, detail="User not found")
return user
```

### 4. Use Async/Await Consistently

**❌ Bad:**
```python
def get_user(db: Session):  # Blocking!
    return db.query(User).all()
```

**✅ Good:**
```python
async def get_user(db: AsyncSession):  # Non-blocking!
    result = await db.execute(select(User))
    return result.scalars().all()
```

### 5. Separate Public and Private Data

**❌ Bad:**
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return user  # Exposes email, phone, etc.!
```

**✅ Good:**
```python
@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int):
    return user  # Only returns public fields
```

---

## Common Patterns

### Dependency Injection

**What is it?**
A way to share code between routes without repeating yourself.

**Example:**
```python
# Define dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Use in route
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    # db is automatically injected
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Response Models

**Control what data is returned:**
```python
@app.get("/users/me", response_model=UserPrivate)
async def get_me(current_user: CurrentUser):
    return current_user  # Includes email, phone

@app.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: int):
    return user  # Excludes email, phone
```

### Status Codes

Use appropriate HTTP status codes:
- `200 OK` - Successful GET/PATCH
- `201 Created` - Successful POST (resource created)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Authenticated but not allowed
- `404 Not Found` - Resource doesn't exist
- `500 Internal Server Error` - Server error

---

## Exercises

### Beginner

1. **Add a "bio" field to User**
   - Update the User model
   - Update UserCreate and UserUpdate schemas
   - Update the registration form
   - Display bio on profile page

2. **Add email validation**
   - Ensure email is lowercase
   - Check email format
   - Prevent duplicate emails (case-insensitive)

3. **Add a "created_at" display**
   - Show when user joined on profile page
   - Format the date nicely

### Intermediate

4. **Implement password change**
   - Create new endpoint: `PATCH /api/users/me/password`
   - Require old password for verification
   - Hash new password before saving

5. **Add profile picture upload**
   - Accept file upload in profile edit
   - Save to media/profile_pics/
   - Generate unique filename
   - Update user.photo field

6. **Add pagination to leaderboard**
   - Add page number parameter
   - Show 10 users per page
   - Add "Next" and "Previous" buttons

### Advanced

7. **Implement password reset**
   - Create reset token (expires in 1 hour)
   - Send email with reset link
   - Verify token and allow password change

8. **Add email verification**
   - Send verification email on registration
   - User can't login until verified
   - Create verification endpoint

9. **Add admin role**
   - Add "is_admin" field to User
   - Create admin-only endpoints
   - Allow admins to manage all users

---

## Further Learning

### Official Documentation
- **FastAPI**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **Pydantic**: https://docs.pydantic.dev

### Recommended Topics
1. **Testing**: Learn pytest for API testing
2. **Migrations**: Use Alembic for database migrations
3. **Deployment**: Deploy to Heroku, Railway, or AWS
4. **Docker**: Containerize your application
5. **CI/CD**: Automate testing and deployment

### Next Steps
1. Complete the exercises above
2. Add your own features
3. Deploy to production
4. Build a different project from scratch

---

**Remember**: The best way to learn is by doing. Don't be afraid to break things and experiment!

Good luck! 🚀
