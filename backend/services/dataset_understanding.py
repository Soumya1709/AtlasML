from pandas import DataFrame


def detect_identifier_columns(dataframe: DataFrame):
    """
    Detect columns that are likely identifiers.
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
        "order",
    ]

    identifier_columns = []

    for column in dataframe.columns:
        column_name = column.lower()

        if any(keyword in column_name for keyword in identifier_keywords):
            identifier_columns.append(column)
            continue

        if dataframe[column].nunique() == len(dataframe):
            identifier_columns.append(column)

    return identifier_columns


def detect_target_column(dataframe: DataFrame):
    """
    Detect the most likely target column.
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
        "exited",
        "default",
        "fraud",
    ]

    for column in dataframe.columns:
        column_name = column.lower()

        if any(keyword in column_name for keyword in target_keywords):
            return column

    last_column = dataframe.columns[-1]

    if dataframe[last_column].nunique() <= 20:
        return last_column

    return None


def detect_problem_type(dataframe: DataFrame, target_column):
    """
    Detect whether the dataset is Classification or Regression.
    """

    if target_column is None:
        return "Unknown"

    target = dataframe[target_column]

    if target.dtype == "object":
        return "Classification"

    if target.nunique() <= 20:
        return "Classification"

    return "Regression"


def detect_datetime_columns(dataframe: DataFrame):
    """
    Detect datetime columns.
    """

    datetime_keywords = [
        "date",
        "time",
        "year",
        "month",
        "day",
        "timestamp",
        "created",
        "updated",
        "dob",
        "birth",
    ]

    datetime_columns = []

    for column in dataframe.columns:
        column_name = column.lower()

        if any(keyword in column_name for keyword in datetime_keywords):
            datetime_columns.append(column)
            continue

        if str(dataframe[column].dtype).startswith("datetime"):
            datetime_columns.append(column)

    return datetime_columns


def detect_text_columns(dataframe: DataFrame):
    """
    Detect long text columns.
    """

    text_columns = []

    for column in dataframe.columns:

        if dataframe[column].dtype != "object":
            continue

        average_length = (
            dataframe[column]
            .dropna()
            .astype(str)
            .str.len()
            .mean()
        )

        if average_length > 30:
            text_columns.append(column)

    return text_columns


def detect_constant_columns(dataframe: DataFrame):
    """
    Detect constant columns.
    """

    constant_columns = []

    for column in dataframe.columns:

        if dataframe[column].nunique(dropna=False) == 1:
            constant_columns.append(column)

    return constant_columns


def detect_high_cardinality_columns(dataframe: DataFrame):
    """
    Detect high-cardinality categorical columns.
    """

    high_cardinality_columns = []

    for column in dataframe.columns:

        if dataframe[column].dtype != "object":
            continue

        unique_ratio = dataframe[column].nunique() / len(dataframe)

        if unique_ratio > 0.5:
            high_cardinality_columns.append(column)

    return high_cardinality_columns


def generate_dataset_problems(summary):
    """
    Generate human-readable dataset issues.
    """

    problems = []

    if summary.get("identifier_columns"):
        problems.append("Identifier columns detected.")

    if summary.get("constant_columns"):
        problems.append("Constant columns detected.")

    if summary.get("high_cardinality_columns"):
        problems.append("High-cardinality columns detected.")

    if summary.get("text_columns"):
        problems.append("Text columns detected.")

    if summary.get("datetime_columns"):
        problems.append("Datetime columns detected.")

    if summary["dataset_quality"]["duplicate_rows"] > 0:
        problems.append("Duplicate rows found.")

    if summary["dataset_quality"]["total_missing_values"] > 0:
        problems.append("Missing values detected.")

    if not problems:
        problems.append("No major dataset problems detected.")

    return problems