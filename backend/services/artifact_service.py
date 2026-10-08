import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.models.artifact import Artifact



def create_artifact(
    db: Session,
    experiment_id: str,
    artifact_name: str,
    artifact_type: str,
    file_path: str,
):
    artifact = Artifact(
        artifact_id=str(uuid4()),
        experiment_id=experiment_id,
        artifact_name=artifact_name,
        artifact_type=artifact_type,
        file_path=file_path,
        created_at=datetime.utcnow(),
    )

    db.add(artifact)
    db.commit()
    db.refresh(artifact)

    return artifact


def get_artifact(
    db: Session,
    artifact_id: str,
):
    return (
        db.query(Artifact)
        .filter(
            Artifact.artifact_id == artifact_id
        )
        .first()
    )


def get_experiment_artifacts(
    db: Session,
    experiment_id: str,
):
    return (
        db.query(Artifact)
        .filter(
            Artifact.experiment_id == experiment_id
        )
        .order_by(Artifact.created_at.asc())
        .all()
    )
    
def save_json_artifact(
    db: Session,
    experiment_id: str,
    artifact_name: str,
    artifact_type: str,
    data: dict,
):
    artifact_dir = Path("artifacts") / experiment_id
    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = artifact_dir / artifact_name

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            default=str,
        )

    return create_artifact(
        db=db,
        experiment_id=experiment_id,
        artifact_name=artifact_name,
        artifact_type=artifact_type,
        file_path=str(file_path),
    )
    
def create_file_artifact(
    db: Session,
    experiment_id: str,
    artifact_name: str,
    artifact_type: str,
    file_path: str,
):
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Artifact file not found: {file_path}"
        )

    return create_artifact(
        db=db,
        experiment_id=experiment_id,
        artifact_name=artifact_name,
        artifact_type=artifact_type,
        file_path=str(path),
    )
    
def save_metrics_artifact(
    db: Session,
    experiment_id: str,
    metrics: dict,
):
    artifact_dir = Path("artifacts") / experiment_id
    artifact_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = artifact_dir / "metrics.json"

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=4,
            default=str,
        )

    return create_artifact(
        db=db,
        experiment_id=experiment_id,
        artifact_name="metrics.json",
        artifact_type="metrics",
        file_path=str(file_path),
    )