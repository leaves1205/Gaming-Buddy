"""File upload under /file"""
# FastAPI routes and file uploads
from fastapi import APIRouter, File, UploadFile

from core.deps import LoginUserDep  # Shared authentication dependency for uploads
from core.files import save_upload  # Shared chunked file storage
from core.response import ajax_error, ajax_success_data  # Shared response builders

router = APIRouter(prefix="/file", tags=["file"])  # Module router


@router.post("/upload")
async def upload_file(login_user: LoginUserDep,
                      file: UploadFile = File(...)):
    """Name an uploaded file with a hyphenless UUID, an underscore, the original stem and the extension"""
    try:  # Return a standard failure response for upload errors
        saved = await save_upload(file, "upload", with_original_stem=True)  # Save the file as UUID_original-stem.extension
        return ajax_success_data({  # Return the fields expected by the frontend upload component
            "url": saved["url"],  # File URL
            "fileName": saved["url"],  # Filename (same as the URL)
            "newFileName": saved["newFileName"],  # Unique stored filename
            "originalFilename": saved["originalFilename"],  # Original filename
        })
    except Exception as e:
        return ajax_error(f"File upload failed: {e}")  # HTTP 200 + code 500
