import re
import io
import pandas as pd
import base64
from datetime import datetime, timedelta
# import streamlit as st


def parse_content(contents, filename):
    print("Received contents:", contents)
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if '.csv' in filename:
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        return df.to_dict('records')
    elif '.xls' in filename:
        df = pd.read_excel(io.BytesIO(decoded))
        return df.to_dict('records')


def decode_image(image_file):
    encoded = base64.b64encode(open(image_file, 'rb').read())
    return f"data:image/png;base64,{encoded.decode()}"



# def clean_dates(df: pd.DataFrame, old_column: str, new_column: str) -> pd.DataFrame:
#     """Cleans a date column with mixed types and unifies format. Creates a new column for the dates"""
#     df[new_column] = pd.to_datetime(df[old_column], errors="coerce", dayfirst=True, format="%d/%m/%Y")  # try date coercion
#     # Coerce date if given in day count format
#     mask = pd.to_numeric(df[old_column], errors="coerce").notna()
#     df.loc[mask, new_column] = pd.to_datetime(df[old_column][mask].astype(float), errors="coerce", unit="D", origin="1899-12-30")
#     return df

def clean_dates(date_str):
    original_value = date_str

    day_first_formats = [
        # Day-First
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%d-%m-%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%d-%m-%y',
        '%d-%m-%y %H:%M:%S',
        '%d/%m/%y',
        '%d/%m/%y %H:%M:%S'
    ]

    month_first_formats = [
        '%m-%d-%Y',
        '%m/%d/%Y',
        '%m-%d-%y',
        '%m-%d-%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%m-%d-%y %H:%M:%S',
    ]

    other_formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d-%b-%y',
        '%d-%b-%Y',
        '%m/%d/%y',
        '%m/%d/%Y',
        '%B %d %Y',
        '%B %d %Y %H:%M:%S'
    ]

    try:
        # try to parse an Excel style date
        excel_date = float(date_str)
        date = datetime(1899, 12, 30) + timedelta(days=excel_date)
        return date.strftime('%Y-%m-%d')
    except ValueError:
        pass

    for date_format in day_first_formats:
        try:
            return datetime.strptime(date_str, date_format).strftime('%Y-%m-%d')
        except ValueError:
            pass

    for date_format in month_first_formats:
        try:
            return datetime.strptime(date_str, date_format).strftime('%Y-%m-%d')
        except ValueError:
            pass

    for date_format in other_formats:
        try:
            return datetime.strptime(date_str, date_format).strftime('%Y-%m-%d')
        except ValueError:
            return original_value


def clean_amounts(amount_str):
    if amount_str == 'nan' or amount_str.strip() == '':
        return 0.0
    try:
        if re.match(r'^\(.+\d\)$', amount_str):  # check amount enclosed in parentheses
            return float('-' + re.sub(r'[^\d./-]', '', amount_str))
        else:
            amount = re.sub(r'[^\d./-]', '', amount_str)  # extract digits, periods and hyphens
            try:
                return float(amount)  # convert amount to float
            except ValueError:
                return amount_str
    except ValueError:
        return amount_str


# @st.cache_data
def clean_dataframe(my_df):
    for col in my_df.columns:
        if 'Unnamed' in col:
            my_df = my_df.drop(col, axis=1)
    for col in my_df.columns:
        my_df[col] = my_df[col].astype(str)
        if 'DATE' in col:
            my_df[col] = my_df[col].apply(clean_dates)
        if 'AMOUNT' in col:
            my_df[col] = my_df[col].apply(clean_amounts)
    date_cols = my_df.filter(like='DATE')
    amount_cols = my_df.filter(like='AMOUNT')
    inconsistent_date = my_df[(my_df['LOSS DATE'] > my_df['PAID DATE']) | (my_df['LOSS DATE'] > my_df['REPORTED DATE'])]
    bad_dates = my_df[date_cols.apply(pd.to_datetime, errors='coerce', dayfirst=False).isna().any(axis=1)]
    bad_amounts = my_df[amount_cols.apply(pd.to_numeric, errors='coerce').isna().any(axis=1)]
    error_df = pd.concat([bad_dates, bad_amounts, inconsistent_date])
    error_df['REFERENCE'] = error_df.index + 2
    error_df = error_df.drop_duplicates().sort_index()
    clean_df = (my_df.drop(error_df.index, axis=0)).reset_index(drop=True)
    return clean_df, error_df

# @st.cache_data
def clean_os_dataframe(my_df):
    for col in my_df.columns:
        if 'Unnamed' in col:
            my_df = my_df.drop(col, axis=1)
    for col in my_df.columns:
        my_df[col] = my_df[col].astype(str)
        if 'DATE' in col:
            my_df[col] = my_df[col].apply(clean_dates)
        if 'AMOUNT' in col:
            my_df[col] = my_df[col].apply(clean_amounts)
    date_cols = my_df.filter(like='DATE')
    amount_cols = my_df.filter(like='AMOUNT')
    inconsistent_date = my_df[(my_df['LOSS DATE'] > my_df['OUTSTANDING DATE']) | (my_df['LOSS DATE'] > my_df['REPORTED DATE'])]
    bad_dates = my_df[date_cols.apply(pd.to_datetime, errors='coerce', dayfirst=False).isna().any(axis=1)]
    bad_amounts = my_df[amount_cols.apply(pd.to_numeric, errors='coerce').isna().any(axis=1)]
    error_df = pd.concat([bad_dates, bad_amounts, inconsistent_date])
    error_df['REFERENCE'] = error_df.index + 2
    error_df = error_df.drop_duplicates().sort_index()
    clean_df = (my_df.drop(error_df.index, axis=0)).reset_index(drop=True)
    return clean_df, error_df
