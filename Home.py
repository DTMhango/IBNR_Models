import pandas as pd
from data_validation import clean_dataframe, clean_os_dataframe
import streamlit as st
import chainladder as cl
from datetime import datetime
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout='wide', page_title='Gralix Actuarial Reserving Interface', page_icon='Gralix Circle.ico')

for k, v in st.session_state.items():
    if k != 'upload':
        st.session_state[k] = v


def logo():
    add_logo("rsz_gralix2.png", height=150)

logo()


@st.cache_data
def convert_df(data_frame):
    # Cache the conversion to prevent computation on every rerun
    return data_frame.to_csv().encode('utf-8')


@st.cache_data
def read_data(data):
    return pd.read_csv(data)


@st.cache_data
def find_index(file_list, match_string):
    for i, file in enumerate(file_list):
        file_name = file.name
        if match_string in file_name:
            return i


# Data to be uploaded - Add to session state
files = ['claims', 'case', 'premium']

for file in files:
    if file not in st.session_state:
        st.session_state[file] = None

min_date = datetime(2000, 1, 1)
max_date = datetime(2030, 12, 31)


uploaded_files = st.sidebar.file_uploader(label='Upload Files',
                                          help='Upload the separate files containing Paid/Incurred Claims Data, '
                                               'Case Reserves Data and Premium Data. Files MUST be ".csv"',
                                          accept_multiple_files=True, key='upload')

if len(st.session_state['upload']) > 0:

    try:
        claims = st.session_state['upload'][find_index(st.session_state['upload'], 'Claims Data')]
        claims_df = read_data(claims)
        clean_df, error_df = clean_dataframe(claims_df)
        st.session_state['claims'] = clean_df
        st.session_state['errors'] = error_df
    except (TypeError, ValueError):
        pass

    try:
        case = st.session_state['upload'][find_index(st.session_state['upload'], 'Outstanding')]
        case_res_df = read_data(case)
        case_df, case_error = clean_os_dataframe(case_res_df)
        for col in case_df.columns:
            if 'Unnamed' in col:
                case_df = case_df.drop(col, axis=1)
        st.session_state['case'] = case_df

    except (TypeError, ValueError):
        pass

    try:
        premium = st.session_state['upload'][find_index(st.session_state['upload'], 'Premium')]
        premium_df = read_data(premium)
        premium_df = premium_df.dropna()
        premium_df = premium_df.set_index(keys='Year', drop=True)
        cols = premium_df.columns

        st.session_state['premium'] = premium_df

    except (TypeError, ValueError):
        pass

claims_data = st.session_state.get('claims')
errors_df = st.session_state.get('errors')
case_data = st.session_state.get('case')
premium_data = st.session_state.get('premium')

if claims_data is not None:
    st.markdown("**USABLE DATA: Clean File**")
    st.dataframe(claims_data)
    clean_csv = convert_df(claims_data)
    download = st.sidebar.download_button(label="Download Clean File",
                                          data=clean_csv,
                                          file_name='Clean.csv',
                                          mime='text/csv')
    if errors_df is not None:
        st.markdown("**UNUSABLE DATA: Error File**")
        st.dataframe(errors_df)
        errors_csv = convert_df(errors_df)
        download = st.sidebar.download_button(label="Download Errors File",
                                              data=errors_csv,
                                              file_name='Errors.csv',
                                              mime='text/csv')

if case_data is not None:
    st.markdown("**CASE RESERVES DATA**")
    st.dataframe(case_data)

if premium_data is not None:
    st.markdown("**PREMIUM DATA**")
    st.dataframe(premium_data)

