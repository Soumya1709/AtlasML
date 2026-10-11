import numpy as np
import pandas as pd

from backend.agents.base_agent import BaseAgent
from backend.logger import logger
from backend.models.pipeline_state import PipelineState


class EDAAgent(BaseAgent):

    def run(self, state: PipelineState) -> PipelineState:
        state.current_agent = "EDAAgent"
        state.status = "running"

        df = state.cleaned_dataframe

        if df is None:
            raise ValueError(
                "EDAAgent requires cleaned_dataframe."
            )

        if df.empty:
            raise ValueError("Cannot perform EDA on an empty dataset.")

        df = df.copy()

        numeric_df = df.select_dtypes(include="number")
        categorical_df = df.select_dtypes(
            include=["object", "category", "bool"]
        )

        numerical_summary = {}
        for column in numeric_df.columns:
            values = numeric_df[column].dropna()

            numerical_summary[column] = {
                "count": int(values.count()),
                "mean": float(values.mean()) if not values.empty else None,
                "median": float(values.median()) if not values.empty else None,
                "std": float(values.std()) if len(values) > 1 else 0.0,
                "min": float(values.min()) if not values.empty else None,
                "max": float(values.max()) if not values.empty else None,
                "skewness": (
                    float(values.skew())
                    if len(values) > 2
                    and np.isfinite(values.skew())
                    else None
                ),
                "outlier_count_iqr": self._outlier_count(values),
            }

        categorical_summary = {}
        for column in categorical_df.columns:
            series = df[column]
            top_values = series.value_counts(dropna=True).head(10)

            categorical_summary[column] = {
                "unique_values": int(series.nunique(dropna=True)),
                "top_values": {
                    str(key): int(value)
                    for key, value in top_values.items()
                },
            }

        missing_values = {
            column: int(count)
            for column, count in df.isna().sum().items()
        }

        correlation_matrix = (
            numeric_df.corr()
            .replace([np.inf, -np.inf], np.nan)
            .fillna(0)
        )

        correlations = {
            column: {
                other: round(float(value), 4)
                for other, value in row.items()
            }
            for column, row in correlation_matrix.to_dict().items()
        }

        observations = []

        missing_columns = [
            column for column, count in missing_values.items()
            if count > 0
        ]
        if missing_columns:
            observations.append(
                f"Missing values remain in {len(missing_columns)} column(s)."
            )

        constant_columns = [
            column for column in df.columns
            if df[column].nunique(dropna=False) <= 1
        ]
        if constant_columns:
            observations.append(
                f"Constant columns detected: {constant_columns}."
            )

        high_cardinality = [
            column for column in categorical_df.columns
            if len(df) > 0
            and df[column].nunique(dropna=True) / len(df) > 0.5
        ]
        if high_cardinality:
            observations.append(
                f"High-cardinality categorical columns: {high_cardinality}."
            )

        duplicate_rows = int(df.duplicated().sum())
        if duplicate_rows:
            observations.append(
                f"{duplicate_rows} duplicate row(s) detected."
            )

        if not observations:
            observations.append(
                "No major issues were detected by the basic EDA checks."
            )

        results = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "numerical_summary": numerical_summary,
            "categorical_summary": categorical_summary,
            "missing_values": missing_values,
            "correlations": correlations,
            "constant_columns": constant_columns,
            "high_cardinality_columns": high_cardinality,
            "duplicate_rows": duplicate_rows,
            "observations": observations,
        }

        state.eda_results = results
        state.summary["eda"] = results
        state.executed_agents.append("EDAAgent")
        state.status = "completed"

        logger.info("EDAAgent completed successfully.")
        return state

    @staticmethod
    def _outlier_count(values: pd.Series) -> int:
        if values.empty:
            return 0

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        if pd.isna(iqr) or iqr == 0:
            return 0

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        return int(((values < lower) | (values > upper)).sum())