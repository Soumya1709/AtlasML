from pandas import DataFrame


def remove_duplicate_rows(dataframe: DataFrame):
    """
    Remove duplicate rows from the dataset.
    """

    cleaned_dataframe = dataframe.drop_duplicates()

    removed_rows = len(dataframe) - len(cleaned_dataframe)

    return cleaned_dataframe, removed_rows