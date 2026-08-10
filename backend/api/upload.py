from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.services.csv_services import (
    read_csv,
    get_dataset_summary,
)
from backend.services.file_service import save_uploaded_file
from backend.services.pipeline_service import execute_pipeline
from backend.services.experiment_service import create_experiment

from backend.database.database import get_db

from backend.config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
)

from backend.schemas.dataset import (
    UploadResponse,
    DatasetSummary,
)

from backend.logger import logger
from backend.models.pipeline_state import PipelineState

router = APIRouter()


@router.post(
    "/upload",
    response_model=UploadResponse,
    tags=["Dataset"],
    summary="Upload CSV Dataset",
    description="Upload a CSV dataset and generate a complete dataset profile.",
)
async def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate file extension
    if not any(
        file.filename.lower().endswith(ext)
        for ext in ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed.",
        )

    # Read file to validate size
    contents = await file.read()

    if len(contents) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Reset file pointer
    await file.seek(0)

    # Validate file size
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum allowed file size is {MAX_FILE_SIZE_MB} MB.",
        )

    logger.info(f"Received upload request: {file.filename}")

    try:
        # Save uploaded CSV
        saved_path = save_uploaded_file(
            file,
            UPLOAD_FOLDER,
        )

        logger.info(f"Dataset saved at: {saved_path}")

        # Read dataset
        dataframe = read_csv(saved_path)

        # Generate dataset summary
        summary = get_dataset_summary(dataframe)

        logger.info("Dataset summary generated successfully.")

        # Create experiment in Neon PostgreSQL
        experiment = create_experiment(
            db=db,
            dataset_name=file.filename,
            dataset_path=saved_path,
        )

        logger.info(
            f"Experiment created successfully: {experiment.experiment_id}"
        )

        # Create pipeline state
        state = PipelineState(
            experiment_id=experiment.experiment_id,
            dataset_path=saved_path,
            summary=summary,
            current_agent="dataset_agent",
            status="running",
        )

        # Execute pipeline
        updated_state = execute_pipeline(
            state=state,
            db=db,
        )

        logger.info(
            f"Pipeline completed with status: {updated_state.status}"
        )

        # Return response
        return UploadResponse(
            original_filename=file.filename,
            saved_path=saved_path,
            summary=DatasetSummary(**updated_state.summary),
        )

    except Exception as e:
        logger.exception("Dataset upload failed")

        raise HTTPException(
            status_code=500,
            detail=f"Unable to process uploaded CSV. Error: {str(e)}",
        )