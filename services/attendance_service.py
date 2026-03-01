from datetime import datetime
from config import Database, Config

class AttendanceService:
    @staticmethod
    def is_allowed_weekday(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.weekday() in Config.ALLOWED_WEEKDAYS

    @staticmethod
    def get_weekday_name(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = date_obj.weekday()
        names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        return names[weekday]

    @staticmethod
    def check_duplicate_attendance(user_id, date_str, shift):
        attendance_collection = Database.get_attendance_collection()
        if attendance_collection is None:
            return False
            
        existing = attendance_collection.find_one({
            "user_id": user_id,
            "date": date_str,
            "shift": shift
        })
        return existing is not None

    @staticmethod
    def log_attendance(user_id, name, date, shift, confidence, image_url=None):
        attendance_collection = Database.get_attendance_collection()
        if attendance_collection is None:
            return False

        attendance_doc = {
            "user_id": user_id,
            "name": name,
            "date": date,
            "shift": shift,
            "shift_name": Config.SHIFTS[shift]["name"],
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "image_url": image_url
        }
        
        attendance_collection.insert_one(attendance_doc)
        return True
