import pandas as pd


def read_csv(file):
    """
    Reads the uploaded CSV file and returns a DataFrame.
    """
    return pd.read_csv(file)


def get_feature_summary(dataframe):
    """
    Categorizes features into numerical, categorical,
    and boolean-like columns.
    """

    numerical = dataframe.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical = dataframe.select_dtypes(
        include=["object"]
    ).columns.tolist()

    boolean_like = []

    for column in dataframe.columns:
        unique_values = dataframe[column].dropna().unique()

        if len(unique_values) == 2:
            boolean_like.append(column)

    return {
        "numerical": numerical,
        "categorical": categorical,
        "boolean_like": boolean_like
    }


def detect_identifier_columns(dataframe):
    """
    Detect identifier columns that should not be used
    for machine learning.
    """

    identifier_keywords = [
        "id",
        "index",
        "row",
        "customer",
        "user",
        "employee",
        "student",
        "transaction",
        "invoice",
        "product",
        "order"
    ]

    identifier_columns = []

    for column in dataframe.columns:

        column_name = column.lower()

        for keyword in identifier_keywords:

            if keyword in column_name:
                identifier_columns.append(column)
                break

        # Check if every value is unique
        if dataframe[column].nunique() == len(dataframe):
            if column not in identifier_columns:
                identifier_columns.append(column)

    return identifier_columns


def detect_target_column(dataframe):
    """
    Attempts to identify the target column
    using common machine learning keywords.
    """

    target_keywords = [
        "target",
        "label",
        "class",
        "output",
        "result",
        "prediction",
        "price",
        "salary",
        "income",
        "survived",
        "species",
        "diagnosis",
        "quality",
        "score",
        "rating",
        "churn",
        "exit",
        "exited"
    ]

    for column in dataframe.columns:

        column_name = column.lower()

        for keyword in target_keywords:

            if keyword in column_name:
                return column

    return None


def get_dataset_summary(dataframe):
    """
    Returns complete dataset profiling information.
    """

    feature_summary = get_feature_summary(dataframe)

    identifier_columns = detect_identifier_columns(dataframe)

    target_column = detect_target_column(dataframe)

    summary = {

        "rows": len(dataframe),

        "columns": len(dataframe.columns),

        "column_names": dataframe.columns.tolist(),

        "identifier_columns": identifier_columns,

        "target_column": target_column,

        "data_types": dataframe.dtypes.astype(str).to_dict(),

        "feature_summary": feature_summary,

        "missing_values": dataframe.isnull().sum().to_dict(),

        "preview": dataframe.head().to_dict(orient="records"),

        "dataset_quality": {

            "duplicate_rows": int(dataframe.duplicated().sum()),

            "total_missing_values": int(
                dataframe.isnull().sum().sum()
            ),

            "missing_percentage": round(
                (
                    dataframe.isnull().sum().sum()
                    / (dataframe.shape[0] * dataframe.shape[1])
                ) * 100,
                2,
            ),

            "memory_usage_mb": round(
                dataframe.memory_usage(deep=True).sum()
                / (1024 * 1024),
                2,
            ),
        },
    }

    return summary