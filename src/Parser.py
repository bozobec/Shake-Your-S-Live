import base64
import io
from datetime import datetime

import pandas as pd
from dash import html, dash_table


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            print("CSV uploaded")
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

    ])


# ToDo: This function is not used. Can it be deleted?
def parse_contents_df(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            print("CSV uploaded")
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)

    return df


def parse_file_contents(contents, filename):
    """
    Improved function for parsing file contents
    :param contents:
    :param filename:
    :return:
    """
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            print("CSV uploaded")
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            print("CSV successfully read")
        elif 'xls' in filename:
            print("XLS uploaded")
            df = pd.read_excel(io.BytesIO(decoded))
            print("XLS successfully read")
        else:
            raise ValueError("Unsupported file format")

        # Remove empty rows
        df.dropna(axis=0, how='all', inplace=True)

    except Exception as e:
        print(e)
        return None

    return df


# ToDo: Function is not used. Can it be deleted?
def parse_file_contents_df(contents, filename, date):
    """
    Improved function to generate DataFrame from contents
    :param contents:
    :param filename:
    :param date:
    :return:
    """
    df = parse_file_contents(contents, filename)
    return df
