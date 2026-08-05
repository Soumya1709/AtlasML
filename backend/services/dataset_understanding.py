from pandas import DataFrame


def detect_identifier_columns(dataframe: DataFrame):
    """
    Detect columns that are likely identifiers
    and should not be used for training.
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
    Detect the most likely target column
    using common machine learning conventions.
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
        "fraud"
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
    Detect whether the dataset is a Classification
    or Regression problem.
    """

    if target_column is None:
        return "Unknown"

    target = dataframe[target_column]

    # Text targets are always classification
    if target.dtype == "object":
        return "Classification"

    unique_values = target.nunique()

    if unique_values <= 20:
        return "Classification"

    return "Regression"

    def detect_datetime_columns(dataframe: DataFrame):
    """
    Detect columns that contain date or time information.
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
        "birth"
    ]

    datetime_columns = []

    for column in dataframe.columns:

        column_name = column.lower()

        # Rule 1: Detect by column name
        if any(keyword in column_name for keyword in datetime_keywords):
            datetime_columns.append(column)
            continue

        # Rule 2: Detect datetime dtype
        if str(dataframe[column].dtype).startswith("datetime"):
            datetime_columns.append(column)

    return datetime_columns

    def detect_text_columns(dataframe: DataFrame):
    """
    Detect columns containing long free-text data.
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
    Detect columns having only one unique value.
    """

    constant_columns = []

    for column in dataframe.columns:

        if dataframe[column].nunique(dropna=False) == 1:
            constant_columns.append(column)

    return constant_columns

def detect_high_cardinality_columns(dataframe: DataFrame):
    """
    Detect categorical columns having too many unique values.
    """

    high_cardinality_columns = []

    for column in dataframe.columns:

        # Only check categorical columns
        if dataframe[column].dtype != "object":
            continue

        unique_ratio = (
            dataframe[column].nunique()
            / len(dataframe)
        )

        # More than 50% unique values
        if unique_ratio > 0.5:
            high_cardinality_columns.append(column)

    return high_cardinality_columns