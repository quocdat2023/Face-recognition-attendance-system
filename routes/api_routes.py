from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
from config import Config, Database

router = APIRouter()

@router.get("/shifts")
async def get_shifts():
    """Get available shifts"""
    return JSONResponse(content={"shifts": Config.SHIFTS})

@router.get("/allowed-days")
async def get_allowed_days():
    """Get allowed weekdays for attendance"""
    return JSONResponse(content={
        "allowed_weekdays": Config.ALLOWED_WEEKDAYS,
        "description": "0=Monday, 2=Wednesday, 4=Friday (Thu 2, Thu 4, Thu 6)"
    })

@router.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        users_collection = Database.get_users_collection()
        attendance_collection = Database.get_attendance_collection()
        
        total_users = users_collection.count_documents({}) if users_collection is not None else 0
        
        today = datetime.now().date().isoformat()
        
        if attendance_collection is not None:
            today_attendance = attendance_collection.count_documents({"date": today})
            
            shift_counts = {}
            for shift_id in Config.SHIFTS:
                count = attendance_collection.count_documents({
                    "date": today,
                    "shift": shift_id
                })
                shift_counts[f"shift_{shift_id}"] = count
        else:
            today_attendance = 0
            shift_counts = {f"shift_{shift_id}": 0 for shift_id in Config.SHIFTS}
            
        return JSONResponse(content={
            "total_users": total_users,
            "today_attendance": today_attendance,
            "shift_counts": shift_counts,
            "today": today
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Lỗi lấy thống kê: {str(e)}"})
