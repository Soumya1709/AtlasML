import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def extract_date_features(
    df: pd.DataFrame,
    datetime_columns: list[str],
) -> tuple[pd.DataFrame, list[str]]:

    df = df.copy()
    created_columns = []

    for column in datetime_columns:

        if column not in df.columns:
            continue

        converted = pd.to_datetime(
            df[column],
            errors="coerce",
        )

        df[f"{column}_year"] = converted.dt.year
        df[f"{column}_month"] = converted.dt.month
        df[f"{column}_day"] = converted.dt.day
        df[f"{column}_dayofweek"] = converted.dt.dayofweek

        created_columns.extend(
            [
                f"{column}_year",
                f"{column}_month",
                f"{column}_day",
                f"{column}_dayofweek",
            ]
        )

        df.drop(
            columns=[column],
            inplace=True,
        )

    return df, created_columns


def build_feature_pipeline(
    df: pd.DataFrame,
    target_column: str | None,
):

    df = df.copy()

    if target_column and target_column in df.columns:

        X = df.drop(
            columns=[target_column]
        )

        y = df[target_column].copy()

    else:

        X = df
        y = None

    numerical_columns = X.select_dtypes(
        include=[
            "int64",
            "int32",
            "float64",
            "float32",
        ]
    ).columns.tolist()

    categorical_columns = X.select_dtypes(
        include=[
            "object",
            "category",
            "bool",
        ]
    ).columns.tolist()

    transformers = []

    if numerical_columns:

        transformers.append(
            (
                "numerical",
                StandardScaler(),
                numerical_columns,
            )
        )

    if categorical_columns:

        transformers.append(
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_columns,
            )
        )

    if not transformers:

        return (
            X,
            X.columns.tolist(),
            None,
            y,
        )

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    transformed = preprocessor.fit_transform(X)

    feature_names = (
        preprocessor
        .get_feature_names_out()
        .tolist()
    )

    transformed_df = pd.DataFrame(
        transformed,
        columns=feature_names,
        index=X.index,
    )

    return (
        transformed_df,
        feature_names,
        preprocessor,
        y,
    )


def select_features(
    feature_df: pd.DataFrame,
    correlation_threshold: float = 0.95,
) -> tuple[
    pd.DataFrame,
    list[str],
    list[dict],
]:

    df = feature_df.copy()

    removed_features = []

    # Remove zero-variance features
    zero_variance_columns = [
        column
        for column in df.columns
        if df[column].nunique(
            dropna=False
        ) <= 1
    ]

    for column in zero_variance_columns:

        removed_features.append(
            {
                "feature": column,
                "reason": "zero_variance",
            }
        )

    if zero_variance_columns:

        df.drop(
            columns=zero_variance_columns,
            inplace=True,
        )

    # Only numerical features participate
    # in correlation filtering
    numerical_columns = [
        column
        for column in df.columns
        if column.startswith("numerical__")
    ]

    numeric_df = df[numerical_columns]

    if numeric_df.shape[1] > 1:

        correlation_matrix = (
            numeric_df
            .corr()
            .abs()
        )

        upper_triangle = (
            correlation_matrix.where(
                np.triu(
                    np.ones(
                        correlation_matrix.shape,
                        dtype=bool,
                    ),
                    k=1,
                )
            )
        )

        for column in upper_triangle.columns:

            correlated_columns = (
                upper_triangle[column][
                    upper_triangle[column]
                    > correlation_threshold
                ]
            )

            for correlated_with in (
                correlated_columns.index
            ):

                removed_features.append(
                    {
                        "feature": column,
                        "reason": "high_correlation",
                        "correlated_with": correlated_with,
                        "correlation": float(
                            round(
                                upper_triangle.loc[
                                    correlated_with,
                                    column,
                                ],
                                4,
                            )
                        ),
                    }
                )

        highly_correlated = [
            column
            for column in upper_triangle.columns
            if any(
                upper_triangle[column]
                > correlation_threshold
            )
        ]

        if highly_correlated:

            df.drop(
                columns=highly_correlated,
                inplace=True,
            )

    selected_features = (
        df.columns.tolist()
    )

    return (
        df,
        selected_features,
        removed_features,
    )


def create_interaction_features(
    df: pd.DataFrame,
    numerical_features: list[str],
    max_features: int = 10,
) -> tuple[pd.DataFrame, list[str]]:

    df = df.copy()

    created_features = []

    numerical_features = [
        column
        for column in numerical_features
        if column in df.columns
    ]

    feature_count = 0

    for i in range(
        len(numerical_features)
    ):

        for j in range(
            i + 1,
            len(numerical_features),
        ):

            if feature_count >= max_features:
                break

            feature_1 = numerical_features[i]
            feature_2 = numerical_features[j]

            new_feature = (
                f"{feature_1}_x_{feature_2}"
            )

            df[new_feature] = (
                df[feature_1]
                * df[feature_2]
            )

            created_features.append(
                new_feature
            )

            feature_count += 1

        if feature_count >= max_features:
            break

    return (
        df,
        created_features,
    )