"""
Shared upload storage

Centralizes UUID naming and disk writes previously implemented in routers/file.py and routers/profile.py.
Call save_upload when a feature needs to write uploaded files to disk.

The naming rules match the existing behavior.
- Avatar (sub_dir="avatar", with_original_stem=False): UUID without hyphens plus the extension
- General upload (sub_dir="upload", with_original_stem=True): UUID without hyphens, underscore, original stem and extension
Read and write in 8,192-byte chunks to limit memory use for large files.
main.py serves files through StaticFiles at /profile/{sub_dir}/{filename}.
"""
import os  # Standard-library file and directory operations
import uuid  # Standard-library unique filename generation

from fastapi import UploadFile  # FastAPI upload type

from core.config import settings  # Read the upload base path

_CHUNK_SIZE = 8192  # Chunk size in bytes (8 KB), balancing memory use and disk writes


def _split_filename(original: str) -> tuple[str, str]:
    """Split a filename into its stem and dotted extension. Use an empty extension if absent."""
    if "." in original:  # The original filename contains a dot
        dot = original.rfind(".")  # Treat the final dot as the extension separator
        return original[:dot], original[dot:]
    return original, ""  # Use the whole filename as the stem if there is no dot


async def save_upload(file: UploadFile, sub_dir: str, with_original_stem: bool = False) -> dict:
    """Save the upload to {profile}/{sub_dir}/ and return {url, newFileName, originalFilename}

    - sub_dir is a subdirectory such as "avatar" or "upload"
    - with_original_stem=True includes the original stem for uploads. False uses only the UUID and extension for avatars.
    - Empty files raise ValueError for the caller to handle
    """
    original_filename = file.filename or ""  # Original filename, which may be empty
    stem, extension = _split_filename(original_filename)  # Split the stem and extension

    # Build a unique filename with a hyphenless UUID and the extension. Include the original stem when requested.
    unique_stem = uuid.uuid4().hex + ("_" + stem if with_original_stem and stem else "")
    unique_filename = unique_stem + extension

    upload_dir = os.path.join(settings.profile, sub_dir)  # Destination directory: {profile}/{sub_dir}
    os.makedirs(upload_dir, exist_ok=True)  # Create the directory if needed

    first = await file.read(_CHUNK_SIZE)  # Read the first chunk to detect an empty file
    if not first:  # Reject empty files
        raise ValueError("The uploaded file is empty")

    file_path = os.path.join(upload_dir, unique_filename)  # Full destination path on disk
    with open(file_path, "wb") as f:  # Open the destination in binary write mode
        f.write(first)  # Write the first chunk
        while chunk := await file.read(_CHUNK_SIZE):  # Read more chunks until the stream is empty
            f.write(chunk)  # Write chunks individually to limit memory use for large files

    return {
        "url": f"/profile/{sub_dir}/{unique_filename}",  # Public URL served by the static mount
        "newFileName": unique_filename,  # Unique stored filename
        "originalFilename": original_filename,  # Original filename
    }
