from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import json
import base64
from datetime import datetime
from config import Database, Config
from services.face_recognition import FaceRecognitionService
from services.cloudinary_service import CloudinaryService

router = APIRouter()

@router.post("/register")
async def register_user(
    name: str = Form(...),
    user_id: str = Form(...),
    images: str = Form(...) 
):
    try:
        users_collection = Database.get_users_collection()
        image_list = json.loads(images)
        
        if len(image_list) < 5:
            raise HTTPException(status_code=400, detail="Cần ít nhất 5 ảnh để đăng ký")
            
        existing_user = users_collection.find_one({"user_id": user_id})
        if existing_user:
            raise HTTPException(status_code=400, detail="Mã số người dùng đã tồn tại")

        face_encodings = []
        failed_count = 0
            
        for i, img_base64 in enumerate(image_list):
            try:
                if ',' in img_base64:
                    img_base64 = img_base64.split(',')[1]
                
                image_bytes = base64.b64decode(img_base64)
                encoding, error = FaceRecognitionService.encode_face_from_image(image_bytes)
                
                if encoding:
                    face_encodings.append(encoding)
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                print(f"Image {i+1} error: {e}")
                
        if len(face_encodings) < 5:
            raise HTTPException(
                status_code=400, 
                detail=f"Không đủ ảnh hợp lệ. Thành công: {len(face_encodings)}, Thất bại: {failed_count}"
            )
            
        image_url = None
        try:
            first_img_base64 = image_list[0]
            if ',' in first_img_base64:
                first_img_base64 = first_img_base64.split(',')[1]
                
            image_bytes = base64.b64decode(first_img_base64)
            image_url = CloudinaryService.upload_image(
                image_bytes, 
                "face_recognition/users", 
                f"user_{user_id}"
            )
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")

        user_doc = {
            "name": name,
            "user_id": user_id,
            "face_encodings": face_encodings,
            "num_encodings": len(face_encodings),
            "image_url": image_url,
            "registered_at": datetime.now().isoformat()
        }
        
        users_collection.insert_one(user_doc)
        
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

@router.get("/users")
async def get_users():
    try:
        users_collection = Database.get_users_collection()
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

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        users_collection = Database.get_users_collection()
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
