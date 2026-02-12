from flask import Flask, render_template, send_from_directory
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import pymongo
from pymongo import MongoClient
import face_recognition
import numpy as np
import cv2
from PIL import Image
import io
import base64
from datetime import datetime
from bson import ObjectId
import os
import json
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

# Load environment variables
load_dotenv()

# Cloudinary Configuration
cloudinary.config( 
  cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'), 
  api_key = os.getenv('CLOUDINARY_API_KEY'), 
  api_secret = os.getenv('CLOUDINARY_API_SECRET'),
  secure = True
)

# ============================================================================
# CONFIGURATION
# ============================================================================

MONGODB_URI = "mongodb://mongo:27017/"
DATABASE_NAME = "face_recognition_db"
USERS_COLLECTION = "users"
ATTENDANCE_COLLECTION = "attendance"
FACE_MATCH_THRESHOLD = 0.6  # Lower is stricter
NUM_IMAGES_FOR_REGISTRATION = 10  # Number of images to capture for registration

# Shift configuration
SHIFTS = {
    1: {"name": "Ca 1", "start": "06:00", "end": "09:00"},
    2: {"name": "Ca 2", "start": "09:00", "end": "12:00"},
    3: {"name": "Ca 3", "start": "13:00", "end": "16:00"},
    4: {"name": "Ca 4", "start": "16:00", "end": "19:00"}
}

# Allowed weekdays (Monday=0, Tuesday=1, ..., Sunday=6)
# Vietnamese: Thu 2=Monday(0), Thu 4=Wednesday(2), Thu 6=Friday(4)
ALLOWED_WEEKDAYS = [0, 2, 4]  # Monday, Wednesday, Friday

# ============================================================================
# FLASK APPLICATION (Frontend)
# ============================================================================

flask_app = Flask(__name__)
flask_app.secret_key = "your-secret-key-change-this"

@flask_app.route('/')
def index():
    """Dashboard/Home page"""
    return render_template('index.html')

@flask_app.route('/register')
def register():
    """User registration page"""
    return render_template('register.html')

@flask_app.route('/recognize')
def recognize():
    """Face recognition/attendance page"""
    return render_template('recognize.html')

@flask_app.route('/attendance')
def attendance():
    """Attendance records page"""
    return render_template('attendance.html')

@flask_app.route('/users')
def users():
    """Registered users page"""
    return render_template('users.html')

# ============================================================================
# FASTAPI APPLICATION (Backend API)
# ============================================================================

api = FastAPI(title="Face Recognition API", version="1.0.0")

# CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
try:
    mongo_client = MongoClient(MONGODB_URI)
    db = mongo_client[DATABASE_NAME]
    users_collection = db[USERS_COLLECTION]
    attendance_collection = db[ATTENDANCE_COLLECTION]
    print(f"✓ Connected to MongoDB: {DATABASE_NAME}")
except Exception as e:
    print(f"✗ MongoDB connection error: {e}")
    mongo_client = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

    id: str
    name: str
    user_id: str
    registered_at: str
    image_url: Optional[str] = None

class FaceLocation(BaseModel):
    top: int
    right: int
    bottom: int
    left: int
    name: str
    confidence: float

class RecognitionResponse(BaseModel):
    faces: List[FaceLocation]
    timestamp: str

class AttendanceRecord(BaseModel):
    id: str
    user_id: str
    name: str
    timestamp: str
    shift: int
    date: str
    image_url: Optional[str] = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def encode_face_from_image(image_bytes):
    """Extract face encoding from image bytes"""
    try:
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_img)
        
        if len(face_locations) == 0:
            return None, "No face detected in image"
        
        if len(face_locations) > 1:
            return None, "Multiple faces detected. Please upload image with single face"
        
        # Get face encoding
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        if len(face_encodings) == 0:
            return None, "Could not encode face"
        
        return face_encodings[0].tolist(), None
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def find_matching_face(face_encoding, threshold=FACE_MATCH_THRESHOLD):
    """Find matching face in database - supports multiple encodings per user"""
    try:
        all_users = list(users_collection.find())
        
        if not all_users:
            return None, 1.0
        
        best_match = None
        best_distance = 1.0
        
        for user in all_users:
            if 'face_encodings' not in user and 'face_encoding' not in user:
                continue
            
            # Support both old format (single encoding) and new format (multiple encodings)
            if 'face_encodings' in user:
                # New format: list of encodings
                stored_encodings = [np.array(enc) for enc in user['face_encodings']]
            else:
                # Old format: single encoding
                stored_encodings = [np.array(user['face_encoding'])]
            
            test_encoding = np.array(face_encoding)
            
            # Calculate distance to all stored encodings and take minimum
            distances = face_recognition.face_distance(stored_encodings, test_encoding)
            min_distance = np.min(distances)
            
            if min_distance < best_distance:
                best_distance = min_distance
                best_match = user
        
        if best_match and best_distance < threshold:
            return best_match, best_distance
        
        return None, best_distance
        
    except Exception as e:
        print(f"Error finding match: {e}")
        return None, 1.0

def is_allowed_weekday(date_str):
    """Check if the given date is Monday, Wednesday, or Friday"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.weekday() in ALLOWED_WEEKDAYS

def get_weekday_name(date_str):
    """Get Vietnamese weekday name"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()
    names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    return names[weekday]

def check_duplicate_attendance(user_id, date_str, shift):
    """Check if user already marked attendance for this shift on this date"""
    existing = attendance_collection.find_one({
        "user_id": user_id,
        "date": date_str,
        "shift": shift
    })
    return existing is not None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@api.post("/register")
async def register_user(
    name: str = Form(...),
    user_id: str = Form(...),
    images: str = Form(...)  # JSON array of base64 images
):
    """Register a new user with multiple face encodings (10 images)"""
    try:
        # Parse images from JSON
        image_list = json.loads(images)
        
        if len(image_list) < 5:
            raise HTTPException(status_code=400, detail="Cần ít nhất 5 ảnh để đăng ký")
        
        # Check if user already exists
        existing_user = users_collection.find_one({"user_id": user_id})
        if existing_user:
            raise HTTPException(status_code=400, detail="Mã số người dùng đã tồn tại")
        
        # Extract face encodings from all images
        face_encodings = []
        failed_count = 0
        
        for i, img_base64 in enumerate(image_list):
            try:
                # Remove data URL prefix if present
                if ',' in img_base64:
                    img_base64 = img_base64.split(',')[1]
                
                # Decode base64 to bytes
                image_bytes = base64.b64decode(img_base64)
                
                # Extract face encoding
                encoding, error = encode_face_from_image(image_bytes)
                
                if encoding:
                    face_encodings.append(encoding)
                else:
                    failed_count += 1
                    print(f"Image {i+1}: {error}")
            except Exception as e:
                failed_count += 1
                print(f"Image {i+1} error: {e}")
        
        if len(face_encodings) < 5:
            raise HTTPException(
                status_code=400, 
                detail=f"Không đủ ảnh hợp lệ. Thành công: {len(face_encodings)}, Thất bại: {failed_count}"
            )
        
        # Upload the first valid image to Cloudinary
        image_url = None
        try:
            # Get the first valid image (we know there's at least one if we're here)
            # Find the first image that resulted in a valid encoding
            # For simplicity, we'll just take the first one from the list that is valid base64
            # Ideally we keep track of which image produced the encoding, but picking the first one is fine for avatar
            
            # Use the first image in the list
            first_img_base64 = image_list[0]
            if ',' in first_img_base64:
                first_img_base64 = first_img_base64.split(',')[1]
                
            image_bytes = base64.b64decode(first_img_base64)
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                image_bytes, 
                folder="face_recognition/users",
                public_id=f"user_{user_id}",
                overwrite=True,
                resource_type="image"
            )
            image_url = upload_result.get("secure_url")
            print(f"Uploaded registration image to Cloudinary: {image_url}")
            
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            # Continue even if upload fails
        
        
        # Save to database
        user_doc = {
            "name": name,
            "user_id": user_id,
            "face_encodings": face_encodings,  # Store list of encodings
            "num_encodings": len(face_encodings),
            "image_url": image_url, # Store Cloudinary URL
            "registered_at": datetime.now().isoformat()
        }
        
        result = users_collection.insert_one(user_doc)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Đăng ký thành công cho {name} với {len(face_encodings)} ảnh",
            "user_id": user_id,
            "image_url": image_url,
            "num_encodings": len(face_encodings)
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Đăng ký thất bại: {str(e)}")

@api.post("/recognize")
async def recognize_faces(
    image: UploadFile = File(...),
    date: str = Form(...),
    shift: int = Form(...)
):
    """Recognize faces and mark attendance with shift validation"""
    try:
        # Validate shift
        if shift not in SHIFTS:
            raise HTTPException(status_code=400, detail=f"Ca trực không hợp lệ. Chọn từ 1-4")
        
        # Validate weekday (Monday, Wednesday, Friday only)
        if not is_allowed_weekday(date):
            weekday_name = get_weekday_name(date)
            raise HTTPException(
                status_code=400, 
                detail=f"Không được phép điểm danh vào {weekday_name}. Chỉ được phép thứ 2, 4, 6"
            )
        
        # Read image
        image_bytes = await image.read()
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find all face locations
        face_locations = face_recognition.face_locations(rgb_img)
        
        if len(face_locations) == 0:
            return JSONResponse(content={
                "faces": [],
                "timestamp": datetime.now().isoformat(),
                "message": "Không phát hiện khuôn mặt"
            })
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        # Match each face
        recognized_faces = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matched_user, distance = find_matching_face(face_encoding.tolist())
            
            if matched_user:
                name = matched_user['name']
                user_id = matched_user['user_id']
                confidence = 1.0 - distance
                
                # Check for duplicate attendance
                if check_duplicate_attendance(user_id, date, shift):
                    status = "already_marked"
                    message = f"{name} đã điểm danh ca {shift} ngày {date}"
                else:
                    # Log attendance
                    
                    # Upload attendance image to Cloudinary
                    attendance_image_url = None
                    try:
                        # Reset file pointer to beginning to read again
                        await image.seek(0)
                        file_content = await image.read()
                        
                        upload_result = cloudinary.uploader.upload(
                            file_content,
                            folder="face_recognition/attendance",
                            public_id=f"attendance_{user_id}_{date}_{shift}_{int(datetime.now().timestamp())}",
                            resource_type="image"
                        )
                        attendance_image_url = upload_result.get("secure_url")
                        print(f"Uploaded attendance image: {attendance_image_url}")
                    except Exception as e:
                        print(f"Error uploading attendance image: {e}")

                    attendance_doc = {
                        "user_id": user_id,
                        "name": name,
                        "date": date,
                        "shift": shift,
                        "shift_name": SHIFTS[shift]["name"],
                        "timestamp": datetime.now().isoformat(),
                        "confidence": confidence,
                        "image_url": attendance_image_url
                    }
                    attendance_collection.insert_one(attendance_doc)
                    status = "success"
                    message = f"Điểm danh thành công: {name} - {SHIFTS[shift]['name']}"
            else:
                name = "Unknown"
                user_id = None
                confidence = 0.0
                status = "unknown"
                message = "Không nhận diện được"
            
            recognized_faces.append({
                "top": int(top),
                "right": int(right),
                "bottom": int(bottom),
                "left": int(left),
                "name": name,
                "user_id": user_id,
                "confidence": float(confidence),
                "status": status,
                "message": message
            })
        
        return JSONResponse(content={
            "faces": recognized_faces,
            "date": date,
            "shift": shift,
            "shift_name": SHIFTS[shift]["name"],
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nhận diện thất bại: {str(e)}")

@api.get("/shifts")
async def get_shifts():
    """Get available shifts"""
    return JSONResponse(content={"shifts": SHIFTS})

@api.get("/allowed-days")
async def get_allowed_days():
    """Get allowed weekdays for attendance"""
    return JSONResponse(content={
        "allowed_weekdays": ALLOWED_WEEKDAYS,
        "description": "0=Monday, 2=Wednesday, 4=Friday (Thu 2, Thu 4, Thu 6)"
    })

@api.get("/users")
async def get_users():
    """Get all registered users"""
    try:
        users = list(users_collection.find({}, {"face_encodings": 0, "face_encoding": 0}))
        
        user_list = []
        for user in users:
            user_list.append({
                "id": str(user['_id']),
                "name": user['name'],
                "user_id": user['user_id'],
                "num_encodings": user.get('num_encodings', 1),
                "registered_at": user['registered_at'],
                "image_url": user.get('image_url')
            })
        
        return JSONResponse(content={"users": user_list})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách: {str(e)}")

@api.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        result = users_collection.delete_one({"user_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Đã xóa người dùng {user_id}"
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Xóa thất bại: {str(e)}")

@api.get("/attendance")
async def get_attendance(limit: int = 100, date: str = None, shift: int = None):
    """Get attendance records with optional filters"""
    try:
        query = {}
        if date:
            query["date"] = date
        if shift:
            query["shift"] = shift
        
        records = list(attendance_collection.find(query).sort("timestamp", -1).limit(limit))
        
        attendance_list = []
        for record in records:
            attendance_list.append({
                "id": str(record['_id']),
                "user_id": record['user_id'],
                "name": record['name'],
                "date": record.get('date', record.get('timestamp', '')[:10]),
                "shift": record.get('shift', 0),
                "shift_name": record.get('shift_name', 'N/A'),
                "timestamp": record['timestamp'],
                "timestamp": record['timestamp'],
                "confidence": record.get('confidence', 0.0),
                "image_url": record.get('image_url')
            })
        
        return JSONResponse(content={"attendance": attendance_list})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy dữ liệu điểm danh: {str(e)}")

@api.delete("/attendance/all")
async def delete_all_attendance():
    """Delete all attendance records"""
    try:
        result = attendance_collection.delete_many({})
        return JSONResponse(content={
            "success": True, 
            "message": f"Đã xóa toàn bộ {result.deleted_count} bản ghi điểm danh"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa dữ liệu: {str(e)}")

@api.delete("/attendance/{record_id}")
async def delete_attendance_record(record_id: str):
    """Delete a specific attendance record"""
    try:
        result = attendance_collection.delete_one({"_id": ObjectId(record_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
            
        return JSONResponse(content={
            "success": True, 
            "message": "Đã xóa bản ghi điểm danh"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa bản ghi: {str(e)}")

@api.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        total_users = users_collection.count_documents({})
        
        # Today's attendance
        today = datetime.now().date().isoformat()
        today_attendance = attendance_collection.count_documents({
            "date": today
        })
        
        # Count by shift today
        shift_counts = {}
        for shift_id in SHIFTS:
            count = attendance_collection.count_documents({
                "date": today,
                "shift": shift_id
            })
            shift_counts[f"shift_{shift_id}"] = count
        
        return JSONResponse(content={
            "total_users": total_users,
            "today_attendance": today_attendance,
            "shift_counts": shift_counts,
            "today": today
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy thống kê: {str(e)}")

# ============================================================================
# MOUNT FASTAPI TO FLASK
# ============================================================================

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from a2wsgi import ASGIMiddleware

# Mount FastAPI app to Flask
# Wrap FastAPI (ASGI) to WSGI using a2wsgi
api_wsgi = ASGIMiddleware(api)
application = DispatcherMiddleware(flask_app, {
    '/api': api_wsgi
})

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Face Recognition System")
    print("=" * 60)
    print("Flask (Frontend): http://localhost:5000")
    print("FastAPI (API): http://localhost:5000/docs")
    print("=" * 60)
    
    # Run combined application
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)
