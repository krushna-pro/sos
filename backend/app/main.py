# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import auth, students, dashboard, bot
from .routes import clusters as clusters_routes
from .routes import admin_counselors as admin_counselors_routes
from .routes import counselor_assigned as counselor_assigned_routes




# Create DB tables on startup (for SQLite this will create a .db file)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Syntax of Success - Dropout Prediction API",
    description="AI-based student dropout prediction & counselling backend",
    version="1.0.0",
)

# Register clusters routes
app.include_router(clusters_routes.router)

# Register admin counselors routes
app.include_router(admin_counselors_routes.router)

# Register counselor assigned routes
app.include_router(counselor_assigned_routes.router)

# CORS: allow frontend (React) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(dashboard.router)
app.include_router(bot.router)


@app.get("/")
def root():
    return {
        "message": "Syntax of Success API is running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}