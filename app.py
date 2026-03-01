import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from flask import Flask, render_template
from fastapi.middleware.wsgi import WSGIMiddleware

from config import Config
from routes import user_routes, attendance_routes, api_routes
from services.cloudinary_service import CloudinaryService

# Initialize services
CloudinaryService.initialize()

# ============================================================================
# FLASK APPLICATION (Frontend)
# ============================================================================

flask_app = Flask(__name__)
flask_app.secret_key = Config.SECRET_KEY

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/register')
def register():
    return render_template('register.html')

@flask_app.route('/recognize')
def recognize():
    return render_template('recognize.html')

@flask_app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@flask_app.route('/users')
def users():
    return render_template('users.html')

# ============================================================================
# FASTAPI APPLICATION (Backend API)
# ============================================================================

api = FastAPI(title="Face Recognition API", version="1.0.0")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
api.include_router(user_routes.router, prefix="/api", tags=["users"])
api.include_router(attendance_routes.router, prefix="/api", tags=["attendance"])
api.include_router(api_routes.router, prefix="/api", tags=["general"])

# ============================================================================
# MOUNT FLASK TO FASTAPI
# ============================================================================

# Mount Flask app to root path "/"
api.mount("/", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    print("=" * 60)
    print("Face Recognition System (Clean Architecture)")
    print("=" * 60)
    print("Application URL: http://localhost:5000")
    print("FastAPI (API):   http://localhost:5000/docs")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run("app:api", host="0.0.0.0", port=5000, reload=True)
