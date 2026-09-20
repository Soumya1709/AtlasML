from typing import List, Dict, Any

from pydantic import BaseModel, Field


class FeatureSummary(BaseModel):

    numerical: List[str]

    categorical: List[str]

    boolean_like: List[str]


class DatasetQuality(BaseModel):

    duplicate_rows: int

    total_missing_values: int

    missing_percentage: float

    memory_usage_mb: float


class DatasetSummary(BaseModel):

    identifier_columns: List[str] = Field(default_factory=list)

    target_column: str | None = None

    problem_type: str = "Unknown"

    datetime_columns: List[str] = Field(default_factory=list)

    text_columns: List[str] = Field(default_factory=list)

    constant_columns: List[str] = Field(default_factory=list)

    high_cardinality_columns: List[str] = Field(default_factory=list)

    dataset_problems: List[str] = Field(default_factory=list)

    rows: int

    columns: int

    column_names: List[str]

    data_types: Dict[str, str]

    feature_summary: FeatureSummary

    missing_values: Dict[str, int]

    preview: List[Dict[str, Any]]

    dataset_quality: DatasetQuality


class UploadResponse(BaseModel):

    original_filename: str

    saved_path: str

    summary: DatasetSummary