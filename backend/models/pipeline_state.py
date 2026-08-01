from typing import Any

from pydantic import BaseModel


class PipelineState(BaseModel):

    dataset_path: str

    summary: dict[str, Any]

    current_agent: str

    status: str

    report: dict[str, Any] | None = None

    trained_model: Any | None = None

    shap_values: Any | None = None

    metrics: dict[str, Any] | None = None