"""
Main FastAPI Application

This is the entry point of the application. It sets up:
- FastAPI app instance
- Database initialization
- Static files and media serving
- Jinja2 templates
- API routers
- HTML page routes

Key Concepts for Interns:
- Application Lifecycle: Startup and shutdown events
- Middleware: Code that runs for every request
- Static Files: CSS, JS, images served directly
- Templates: Server-side HTML rendering
- Routing: Organizing endpoints
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from database import engine, Base
from routers import auth, users, leaderboard, farmservice
from routers.aihelp import router as aihelp_router
from routers.challenge import router as challenge_router
# Import models so they register with Base.metadata before create_all
import models.conversation  # noqa: F401
import models.plant_discovery  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Manager
    
    This function handles startup and shutdown events for the application.
    It uses an async context manager to ensure proper resource cleanup.
    
    Startup (before yield):
    - Create database tables if they don't exist
    - Initialize connections
    - Load configuration
    
    Shutdown (after yield):
    - Close database connections
    - Clean up resources
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None: Control to the application
    """
    # Startup: Create database tables
    print("[STARTUP] Starting up application...")
    async with engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)
    print("[STARTUP] Database tables created")
    
    yield  # Application runs here
    
    # Shutdown: Clean up resources
    print("[SHUTDOWN] Shutting down application...")
    await engine.dispose()
    print("[SHUTDOWN] Database connections closed")


# Create FastAPI application instance
app = FastAPI(
    title="FastAPI User Management",
    description="A complete user management system with authentication, authorization, and leaderboard",
    version="1.0.0",
    lifespan=lifespan,  # Attach lifespan manager
)


# Mount static files
# Static files are served directly without processing (CSS, JS, images)
# URL: /static/... → Directory: static/...
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount media files (user uploads)
# URL: /media/... → Directory: media/...
app.mount("/media", StaticFiles(directory="media"), name="media")


# Set up Jinja2 templates
# Templates are HTML files with dynamic content
templates = Jinja2Templates(directory="templates")


# Include API routers
# These handle all the REST API endpoints
app.include_router(auth.router)  # /api/auth/*
app.include_router(users.router)  # /api/users/*
app.include_router(leaderboard.router)  # /api/leaderboard/*
app.include_router(farmservice.router)  # /farmservice and /api/farmservice/*
app.include_router(aihelp_router)  # /aihelp/*
app.include_router(challenge_router)  # /challenge/*


# ============================================================================
# HTML Page Routes
# These routes serve HTML pages (not API endpoints)
# ============================================================================

@app.get("/", include_in_schema=False)
async def home(request: Request):
    """
    Home page - displays the landing page.
    
    This is the main landing page with features, stats, and call-to-action.
    """
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"title": "Home"}
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """
    Login page.
    
    Displays a login form where users can enter their email and password.
    The form submits to the API endpoint /api/auth/token.
    """
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"title": "Login"}
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    """
    Registration page.
    
    Displays a registration form where new users can create an account.
    The form submits to the API endpoint /api/auth/register.
    """
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"title": "Register"}
    )


@app.get("/dashboard", include_in_schema=False)
async def dashboard_page(request: Request):
    """
    User dashboard page.
    
    Displays the current user's profile information.
    This is a protected page - JavaScript checks authentication.
    """
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"title": "Dashboard"}
    )


@app.get("/profile/edit", include_in_schema=False)
async def profile_edit_page(request: Request):
    """
    Profile editing page.
    
    Allows users to update their profile information.
    This is a protected page - JavaScript checks authentication.
    """
    return templates.TemplateResponse(
        request=request,
        name="profile_edit.html",
        context={"title": "Edit Profile"}
    )


@app.get("/leaderboard", include_in_schema=False)
async def leaderboard_page(request: Request):
    """
    Leaderboard page.
    
    Displays all users sorted by points.
    This is a public page - no authentication required.
    """
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"title": "Leaderboard"}
    )


@app.get("/profile/{user_id}", include_in_schema=False)
async def profile_page(request: Request, user_id: int):
    """
    User profile page.
    
    Displays a specific user's public profile.
    This is a public page - no authentication required.
    
    Args:
        user_id: ID of the user to display
    """
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"title": "User Profile", "user_id": user_id}
    )


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    # This is only used when running the file directly (python main.py)
    # In production, use: uvicorn main:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only!)
        log_level="info"
    )


# Best Practices for Interns:
#
# 1. Application Structure:
#    - Separate API routes from HTML routes
#    - Use routers to organize related endpoints
#    - Keep main.py clean and focused on setup
#
# 2. Static Files:
#    - Static files are cached by browsers for performance
#    - Use versioning for cache busting (e.g., style.css?v=1.0.0)
#    - Serve from CDN in production for better performance
#
# 3. Templates:
#    - Templates are rendered server-side
#    - Use context to pass data to templates
#    - Keep templates simple, move logic to JavaScript
#
# 4. Lifespan Events:
#    - Use for database connections, cache initialization, etc.
#    - Always clean up resources in shutdown
#    - Don't put heavy operations here (slows startup)
#
# 5. Running the App:
#    - Development: uvicorn main:app --reload
#    - Production: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
#    - Use environment variables for configuration
#
# 6. API Documentation:
#    - FastAPI auto-generates docs at /docs (Swagger UI)
#    - Also available at /redoc (ReDoc)
#    - include_in_schema=False hides HTML routes from API docs
