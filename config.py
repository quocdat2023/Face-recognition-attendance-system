import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "face_recognition_db")
    USERS_COLLECTION = "users"
    ATTENDANCE_COLLECTION = "attendance"

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # Application Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    FACE_MATCH_THRESHOLD = 0.6
    NUM_IMAGES_FOR_REGISTRATION = 10

    # Shift configuration
    SHIFTS = {
        1: {"name": "Ca 1", "start": "06:00", "end": "09:00"},
        2: {"name": "Ca 2", "start": "09:00", "end": "12:00"},
        3: {"name": "Ca 3", "start": "13:00", "end": "16:00"},
        4: {"name": "Ca 4", "start": "16:00", "end": "19:00"}
    }

    # Allowed weekdays (Monday=0, Tuesday=1, ..., Sunday=6)
    ALLOWED_WEEKDAYS = [0,  2, 4]  # Monday, Wednesday, Friday

class Database:
    client = None
    db = None

    @classmethod
    def connect(cls):
        try:
            cls.client = MongoClient(Config.MONGODB_URI)
            cls.db = cls.client[Config.DATABASE_NAME]
            print(f"✓ Connected to MongoDB: {Config.DATABASE_NAME}")
        except Exception as e:
            print(f"✗ MongoDB connection error: {e}")

    @classmethod
    def get_users_collection(cls):
        return cls.db[Config.USERS_COLLECTION] if cls.db is not None else None

    @classmethod
    def get_attendance_collection(cls):
        return cls.db[Config.ATTENDANCE_COLLECTION] if cls.db is not None else None

# Initialize DB connect
Database.connect()
