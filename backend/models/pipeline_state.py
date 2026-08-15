from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class PipelineState(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_path: str
    summary: dict[str, Any]
    current_agent: str
    status: str

    executed_agents: list[str] = Field(
        default_factory=list
    )

    cleaned_dataset: Any | None = None
    cleaned_dataframe: Any | None = None

    selected_features: list[str] | None = None
    trained_model: Any | None = None
    metrics: dict[str, Any] | None = None
    shap_values: Any | None = None
    report: dict[str, Any] | None = None

    experiment_id: str