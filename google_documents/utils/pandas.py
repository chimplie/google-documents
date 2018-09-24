from pandas import DataFrame

from google_documents.entities.file import GoogleDriveSpreadsheet


def data_frame_to_google_spreadsheet(
        data_frame: DataFrame,
        spreadsheet_id,
        range_name,
        google_service_account_file=None,
        fillna='',
        include_index=True,
        include_columns=True,
        value_input_option=None
):
    """
    Writes pandas data frame in the Google Spreadsheet
    :param data_frame: Pandas dataframe with data
    :param spreadsheet_id: ID of the spreadsheet to write
    :param range_name: Range name for the data
    :param google_service_account_file: WIP
    :param fillna: value by which to replace dataframe NA values
    :param include_index: True if write data frame index to the spreadsheet
    :param include_columns: True if write data frame column to the spreadsheet
    :param value_input_option: 'RAW' if you want
    to allow Google Sheets to format your values,
    'USER_ENTERED' to keep values in the same format
    :return:
    """
    if include_index:
        # Resetting index will append index
        # To the first rows of data frame values
        data_frame_to_write = data_frame.reset_index()
    else:
        # Otherwise we just copying the dataframe
        data_frame_to_write = data_frame.copy()

    # Filling all na values
    data_frame_to_write = data_frame_to_write.fillna(fillna)

    # Getting list of data frame columns
    data_frame_values_list = data_frame.values.tolist()

    # Appending columns at the top of the values list
    if include_columns:
        data_frame_values_list.insert(0, data_frame_to_write.columns)

    # Initializing Google Spreadsheet
    spreadsheet_manager = GoogleDriveSpreadsheet.objects()

    # Using custom credentials
    if google_service_account_file:
        spreadsheet_manager.using(google_service_account_file)

    spreadsheet = spreadsheet_manager.get(id=spreadsheet_id)
    if not spreadsheet:
        raise ValueError("Spreadsheet `id` is not valid. "
                         "Spreadsheet may not exist or "
                         "service account may not have access to it")

    spreadsheet.write(
        range_name=range_name,
        data=data_frame_values_list,
        value_input_option=value_input_option
    )


def google_spreadsheet_to_data_frame(
        spreadsheet_id,
        range_name,
        google_service_account_file=None,
        skip_rows=0,
        first_row_as_columns=True,
        first_column_as_index=False

):
    spreadsheet_manager = GoogleDriveSpreadsheet.objects()

    # Using custom service account if needed
    if google_service_account_file:
        spreadsheet_manager.using(google_service_account_file)

    spreadsheet = spreadsheet_manager.get(id=spreadsheet_id)
    if not spreadsheet:
        raise ValueError("Spreadsheet `id` is not valid. "
                         "Spreadsheet may not exist or "
                         "service account may not have access to it")

    data: list = spreadsheet.read(range_name=range_name)

    if skip_rows:
        data = data[skip_rows:]

    columns = None
    if first_row_as_columns:
        if len(data) == 0:
            raise ValueError(
                "Cannot extract columns from the empty Spreadsheet data")

        columns = data.pop(0)

    index = None
    if first_column_as_index:
        index = []
        for row in data:
            if len(row) == 0:
                raise ValueError(
                    "Cannot extract index name from the empty data row")
            index.append(row.pop(0))

    return DataFrame.from_records(data, index=index, columns=columns)
