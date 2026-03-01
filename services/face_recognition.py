import cv2
import numpy as np
import face_recognition
from config import Database, Config

class FaceRecognitionService:
    @staticmethod
    def encode_face_from_image(image_bytes):
        """Extract face encoding from image bytes"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_img)
            
            if len(face_locations) == 0:
                return None, "No face detected in image"
            
            if len(face_locations) > 1:
                return None, "Multiple faces detected. Please upload image with single face"
            
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            
            if len(face_encodings) == 0:
                return None, "Could not encode face"
            
            return face_encodings[0].tolist(), None
        except Exception as e:
            return None, f"Error processing image: {str(e)}"

    @staticmethod
    def extract_all_faces(image_bytes):
        """Extract all face encodings and locations from an image"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_img)
            
            if len(face_locations) == 0:
                return [], [], "No face detected"
                
            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            return face_locations, face_encodings, None
        except Exception as e:
            return [], [], str(e)

    @staticmethod
    def find_matching_face(face_encoding, threshold=None):
        """Find matching face in database"""
        if threshold is None:
            threshold = Config.FACE_MATCH_THRESHOLD
            
        try:
            users_collection = Database.get_users_collection()
            if users_collection is None:
                return None, 1.0

            all_users = list(users_collection.find())
            
            if not all_users:
                return None, 1.0
            
            best_match = None
            best_distance = 1.0
            test_encoding = np.array(face_encoding)
            
            for user in all_users:
                if 'face_encodings' not in user and 'face_encoding' not in user:
                    continue
                
                if 'face_encodings' in user:
                    stored_encodings = [np.array(enc) for enc in user['face_encodings']]
                else:
                    stored_encodings = [np.array(user['face_encoding'])]
                
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
