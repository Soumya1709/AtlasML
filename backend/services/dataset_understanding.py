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