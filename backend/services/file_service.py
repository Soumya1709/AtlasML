import os
import shutil
import uuid


def save_uploaded_file(file, upload_folder):
    """
    Saves the uploaded file with a unique filename and
    returns the saved file path.
    """

    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"

    # Full file path
    file_path = os.path.join(upload_folder, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path