from typing import Any
from pydantic import BaseModel


class PipelineState(BaseModel):

    dataset_path: str

    summary: dict[str, Any]

    current_agent: str

    status: str

    cleaned_dataset: Any | None = None

    selected_features: list[str] | None = None

    trained_model: Any | None = None

    metrics: dict[str, Any] | None = None

    shap_values: Any | None = None

    report: dict[str, Any] | None = None