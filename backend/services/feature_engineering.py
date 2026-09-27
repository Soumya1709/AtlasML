import pandas as pd

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

        converted = pd.to_datetime(df[column], errors="coerce")

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

        df.drop(columns=[column], inplace=True)

    return df, created_columns


def build_feature_pipeline(
    df: pd.DataFrame,
    target_column: str | None,
):
    df = df.copy()

    if target_column and target_column in df.columns:
        X = df.drop(columns=[target_column])
        y = df[target_column]
    else:
        X = df
        y = None

    numerical_columns = X.select_dtypes(
        include=["int64", "int32", "float64", "float32"]
    ).columns.tolist()

    categorical_columns = X.select_dtypes(
        include=["object", "category", "bool"]
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

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    transformed = preprocessor.fit_transform(X)

    feature_names = preprocessor.get_feature_names_out().tolist()

    transformed_df = pd.DataFrame(
        transformed,
        columns=feature_names,
        index=df.index,
    )

    if y is not None:
        transformed_df[target_column] = y.values

    return transformed_df, feature_names, preprocessor