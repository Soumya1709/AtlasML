from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class PipelineState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset_path: str
    summary: dict[str, Any]
    current_agent: str
    status: str
    executed_agents: list[str] = Field(default_factory=list)

    cleaned_dataset: Any | None = None
    cleaned_dataframe: Any | None = None

    selected_features: list[str] | None = None
    selected_models: dict[str, Any] | None = None
    
    X_train: Any | None = None
    X_test: Any | None = None
    y_train: Any | None = None
    y_test: Any | None = None

    trained_models: dict[str, Any] | None = None
    best_model: Any | None = None
    best_model_name: str | None = None
    tuning_results: dict[str, Any] | None = None

    feature_dataframe: Any | None = None
    feature_metadata: dict[str, Any] | None = None
    feature_preprocessor: Any | None = None
    target_values: Any | None = None

    trained_model: Any | None = None
    metrics: dict[str, Any] | None = None
    shap_values: Any | None = None
    report: dict[str, Any] | None = None
    eda_results: dict[str, Any] | None = None
    deployment: dict[str, Any] | None = None

    experiment_id: str