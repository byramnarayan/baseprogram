# FastAPI User Management - Industry Standard Learning Project

A complete, production-ready FastAPI application designed as an educational resource for interns learning modern web development with Python.

## 🎯 Project Overview

This project demonstrates industry-standard practices for building a full-stack web application with:
- **Backend**: FastAPI with async SQLAlchemy
- **Authentication**: JWT tokens with OAuth2
- **Database**: SQLite (development) → PostgreSQL-ready (production)
- **Frontend**: Jinja2 templates with Tailwind CSS
- **Security**: Password hashing with Argon2, proper authorization

## ✨ Features

- ✅ User registration and authentication
- ✅ JWT-based session management
- ✅ Profile management (view, edit, delete)
- ✅ Points-based leaderboard system
- ✅ Responsive UI with Tailwind CSS
- ✅ RESTful API design
- ✅ Comprehensive inline documentation
- ✅ Industry-standard project structure

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Basic understanding of Python and web development

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
cd baseprogram
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📁 Project Structure

```
baseprogram/
├── models/              # Database models (SQLAlchemy)
│   └── user.py         # User model definition
├── schemas/            # Pydantic schemas (validation)
│   ├── user.py        # User request/response schemas
│   └── auth.py        # Authentication schemas
├── routers/            # API endpoints (organized by feature)
│   ├── auth.py        # Authentication routes
│   ├── users.py       # User management routes
│   └── leaderboard.py # Leaderboard routes
├── templates/          # HTML templates (Jinja2)
│   ├── base.html      # Base template with navbar
│   ├── login.html     # Login page
│   ├── register.html  # Registration page
│   ├── dashboard.html # User dashboard
│   ├── profile_edit.html # Profile editing
│   ├── leaderboard.html  # Leaderboard display
│   ├── profile.html   # Public profile view
│   └── error.html     # Error page
├── static/             # Static files (CSS, JS, images)
│   ├── css/           # Custom CSS
│   ├── js/            # JavaScript modules
│   │   ├── auth.js    # Authentication utilities
│   │   └── utils.js   # Helper functions
│   └── profile_pics/  # Default profile pictures
├── media/              # User uploads
│   └── profile_pics/  # Uploaded profile pictures
├── main.py             # FastAPI application entry point
├── database.py         # Database configuration
├── auth.py             # Authentication logic
├── config.py           # Application settings
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (SECRET_KEY, etc.)
└── .gitignore          # Git ignore rules
```

## 🔑 Key Concepts Demonstrated

### 1. **Async Python**
All database operations use async/await for better performance:
```python
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### 2. **Dependency Injection**
FastAPI's dependency system for database sessions and authentication:
```python
@router.get("/me")
async def get_current_user(current_user: CurrentUser):
    return current_user
```

### 3. **Pydantic Validation**
Automatic request/response validation:
```python
class UserCreate(BaseModel):
    email: EmailStr  # Automatically validates email format
    password: str = Field(min_length=8)  # Enforces minimum length
```

### 4. **Security Best Practices**
- Password hashing with Argon2
- JWT tokens for stateless authentication
- CORS protection
- Input validation
- SQL injection prevention (via ORM)

### 5. **RESTful API Design**
- Proper HTTP methods (GET, POST, PATCH, DELETE)
- Meaningful status codes (200, 201, 400, 401, 404)
- Resource-based URLs
- Consistent response formats

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/token` - Login and get JWT token
- `POST /api/auth/logout` - Logout (client-side)

### Users
- `GET /api/users/me` - Get current user profile (protected)
- `PATCH /api/users/me` - Update current user (protected)
- `DELETE /api/users/me` - Delete account (protected)
- `GET /api/users/{user_id}` - View public profile

### Leaderboard
- `GET /api/leaderboard` - Get users ranked by points

For detailed API documentation, visit http://localhost:8000/docs after starting the server.

## 🎓 Learning Resources

- **LEARNING.md** - Comprehensive guide for interns
- **Inline Comments** - Every file has detailed explanations
- **API Docs** - Interactive Swagger UI at /docs
- **Code Examples** - Real-world patterns throughout

## 🛠️ Development Workflow

### 1. Make Changes
Edit files in your preferred code editor (VS Code, PyCharm, etc.)

### 2. Test Locally
The `--reload` flag automatically restarts the server when you save changes:
```bash
uvicorn main:app --reload
```

### 3. Check API Docs
Visit http://localhost:8000/docs to test your API changes interactively

### 4. Test in Browser
Navigate to http://localhost:8000 to test the UI

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**Important**: Never commit `.env` to version control!

### Generate a Secure Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

## 🚀 Production Deployment

### 1. Switch to PostgreSQL
Update `database.py`:
```python
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
```

### 2. Set Environment Variables
```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql+asyncpg://..."
```

### 3. Run with Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 4. Use HTTPS
Always use HTTPS in production to protect JWT tokens and passwords.

## 📝 Common Tasks

### Create a New User (via API)
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "password": "SecurePass123"
  }'
```

### Login and Get Token
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=SecurePass123"
```

### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐛 Troubleshooting

### Database Locked Error
SQLite doesn't handle concurrent writes well. For production, use PostgreSQL.

### Module Not Found
Make sure you've activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
```

### Port Already in Use
Change the port in `main.py` or kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill
```

## 🤝 Contributing

This is an educational project. Feel free to:
- Add new features
- Improve documentation
- Fix bugs
- Suggest enhancements

## 📄 License

This project is created for educational purposes. Feel free to use it for learning and teaching.

## 🎯 Next Steps for Interns

1. **Understand the Code**: Read through all files, starting with `main.py`
2. **Experiment**: Try adding new fields to the User model
3. **Build Features**: Add password reset, email verification, etc.
4. **Learn Testing**: Write unit tests for the API endpoints
5. **Deploy**: Try deploying to Heroku, Railway, or AWS

## 📞 Support

For questions or issues:
1. Check the inline comments in the code
2. Read LEARNING.md for detailed explanations
3. Consult the API documentation at /docs
4. Review FastAPI official docs: https://fastapi.tiangolo.com

---

**Built with ❤️ for learning FastAPI and modern web development**
