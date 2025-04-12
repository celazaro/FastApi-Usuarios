import os
from fastapi import UploadFile # type: ignore
from PIL import Image
from pathlib import Path
import shutil
import uuid

# Crear directorio media si no existe
MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

async def save_image(file: UploadFile) -> str:
    """
    Guarda una imagen subida y retorna la ruta relativa donde se guardó
    """
    # Verificar la extensión del archivo
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Tipo de archivo no permitido")
    
    # Crear un nombre único para el archivo
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = MEDIA_DIR / unique_filename
    
    # Guardar el archivo
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Optimizar la imagen
    with Image.open(file_path) as img:
        # Mantener una calidad razonable pero optimizada
        img.save(file_path, optimize=True, quality=85)
    
    # Retornar la ruta relativa
    return str(file_path)

async def delete_image(image_path: str):
    """
    Elimina una imagen del sistema de archivos
    """
    if image_path:
        path = Path(image_path)
        if path.exists():
            path.unlink()