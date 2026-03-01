import cloudinary
import cloudinary.uploader
from config import Config

class CloudinaryService:
    @staticmethod
    def initialize():
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
            secure=True
        )
        print("✓ Cloudinary initialized")

    @staticmethod
    def upload_image(image_bytes, folder: str, public_id: str):
        try:
            upload_result = cloudinary.uploader.upload(
                image_bytes,
                folder=folder,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            return upload_result.get("secure_url")
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            return None
