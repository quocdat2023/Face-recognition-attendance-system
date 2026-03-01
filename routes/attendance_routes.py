from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from bson import ObjectId
from config import Config, Database
from services.face_recognition import FaceRecognitionService
from services.attendance_service import AttendanceService
from services.cloudinary_service import CloudinaryService

router = APIRouter()

@router.post("/recognize")
async def recognize_faces(
    image: UploadFile = File(...),
    date: str = Form(...),
    shift: int = Form(...)
):
    try:
        if shift not in Config.SHIFTS:
            raise HTTPException(status_code=400, detail=f"Ca trực không hợp lệ. Chọn từ 1-4")
            
        if not AttendanceService.is_allowed_weekday(date):
            weekday_name = AttendanceService.get_weekday_name(date)
            raise HTTPException(
                status_code=400, 
                detail=f"Không được phép điểm danh vào {weekday_name}. Chỉ được phép thứ 2, 4, 6"
            )

        image_bytes = await image.read()
        face_locations, face_encodings, error = FaceRecognitionService.extract_all_faces(image_bytes)
        
        if error:
            return JSONResponse(content={
                "faces": [],
                "timestamp": datetime.now().isoformat(),
                "message": error
            })
            
        recognized_faces = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matched_user, distance = FaceRecognitionService.find_matching_face(face_encoding.tolist())
            
            if matched_user:
                name = matched_user['name']
                user_id = matched_user['user_id']
                confidence = 1.0 - distance
                
                if AttendanceService.check_duplicate_attendance(user_id, date, shift):
                    status = "already_marked"
                    message = f"{name} đã điểm danh ca {shift} ngày {date}"
                else:
                    attendance_image_url = None
                    try:
                        await image.seek(0)
                        file_content = await image.read()
                        attendance_image_url = CloudinaryService.upload_image(
                            file_content,
                            "face_recognition/attendance",
                            f"attendance_{user_id}_{date}_{shift}_{int(datetime.now().timestamp())}"
                        )
                    except Exception as e:
                        print(f"Error uploading attendance image: {e}")

                    AttendanceService.log_attendance(user_id, name, date, shift, confidence, attendance_image_url)
                    status = "success"
                    message = f"Điểm danh thành công: {name} - {Config.SHIFTS[shift]['name']}"
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
            "shift_name": Config.SHIFTS[shift]["name"],
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nhận diện thất bại: {str(e)}")

@router.get("/attendance")
async def get_attendance(limit: int = 100, date: str = None, shift: int = None):
    try:
        attendance_collection = Database.get_attendance_collection()
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
                "confidence": record.get('confidence', 0.0),
                "image_url": record.get('image_url')
            })
            
        return JSONResponse(content={"attendance": attendance_list})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy dữ liệu điểm danh: {str(e)}")

@router.delete("/attendance/all")
async def delete_all_attendance():
    try:
        attendance_collection = Database.get_attendance_collection()
        result = attendance_collection.delete_many({})
        return JSONResponse(content={
            "success": True, 
            "message": f"Đã xóa toàn bộ {result.deleted_count} bản ghi điểm danh"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa dữ liệu: {str(e)}")

@router.delete("/attendance/{record_id}")
async def delete_attendance_record(record_id: str):
    try:
        attendance_collection = Database.get_attendance_collection()
        result = attendance_collection.delete_one({"_id": ObjectId(record_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi")
            
        return JSONResponse(content={
            "success": True, 
            "message": "Đã xóa bản ghi điểm danh"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xóa bản ghi: {str(e)}")
