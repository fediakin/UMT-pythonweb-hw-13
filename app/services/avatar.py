"""
Сервіс для завантаження аватарів у Cloudinary.
"""
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLD_NAME", "name"),
    api_key=os.getenv("CLD_API_KEY", "key"),
    api_secret=os.getenv("CLD_API_SECRET", "secret"),
    secure=True
)

def upload_avatar(file, public_id: str) -> str:
    """
    Завантажує файл у Cloudinary та повертає URL зображення.
    """
    r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop='fill', version=r.get('version')
    )
    return url