import pandas as pd
from data_validation import clean_dataframe, decode_image
import streamlit as st
import chainladder as cl
from datetime import datetime
from cl_module import create_triangles
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout='wide', page_title='Gralix Actuarial Reserving Interface', page_icon='Gralix Circle.ico')

for k, v in st.session_state.items():
    st.session_state[k] = v


def logo():
    add_logo("rsz_gralix2.png", height=150)

logo()

claims_data = st.session_state.get('claims')
errors_df = st.session_state.get('errors')
case_data = st.session_state.get('case')
premium_data = st.session_state.get('premium')

st.subheader(':lock: This Page is Currently Locked')
