import pandas as pd
import streamlit as st
import chainladder as cl
from datetime import datetime
from cl_module import create_triangles, create_os_triangles, pure_ibnr
from streamlit_extras.app_logo import add_logo

st.set_page_config(layout='wide', page_title='Gralix Actuarial Reserving Interface', page_icon='Gralix Circle.ico')

for k, v in st.session_state.items():
    st.session_state[k] = v


def logo():
    add_logo("rsz_gralix2.png", height=150)

logo()

@st.cache_data
def convert_df(data_frame):
    # Cache the conversion to prevent computation on every rerun
    return data_frame.to_csv().encode('utf-8')

# logo = decode_image('Gralix Logo.png')
# st.sidebar.image(logo)

claims_data = st.session_state.get('claims')
errors_df = st.session_state.get('errors')
case_data = st.session_state.get('case')
premium_data = st.session_state.get('premium')

min_date = datetime(2000, 1, 1)
max_date = datetime(2030, 12, 31)


if claims_data is not None:
    set_dates = st.date_input('Select your Date Range', (min_date, max_date), key='dates') # SET DATA DATES
    triangles = create_triangles(claims_data, str(set_dates[0]), str(set_dates[1])) # CREATE TRIANGLES
    if case_data is not None:
        os_triangle = create_os_triangles(case_data, str(set_dates[0]), str(max_date)) # CREATE OS_TRIANGLES IF DATA EXISTS
    classes_of_business = claims_data['MAIN CLASS'].unique() # IDENTIFY UNIQUE BUSINESS CLASSES
    add_dimension = claims_data['ADDITIONAL SEGMENTATION'].unique() # IDENTIFY ADDITIONAL SEGMENTATION
    segments = ['No Segmentation'] # ASSUME NO ADDITIONAL SEGMENTATION
    cob = st.selectbox(label='Main Class', options=classes_of_business, key='class-of-business')
    if add_dimension.size==1 and add_dimension[0] == 'nan':
        segments = segments
        segment = st.selectbox(label='Additional Segmentation', options=segments) # CREATE SEGEMENTATION LIST IF APPLICABLE
    else:
        segments.extend(add_dimension)
        segment = st.selectbox(label='Additional Segmentation', options=segments)

    gross_net = st.radio('Select Gross or Net Triangles', options=['Gross', 'Net'], horizontal=True)
    t_grain = st.radio('Select Triangle Grain', options=['OYDY', 'OYDS', 'OYDQ', 'OYDM',
                                                         'OSDS', 'OSDQ', 'OSDM',
                                                         'OQDQ', 'OQDM',
                                                         'OMDM'], horizontal=True, key='triangle-grain')
    view = st.radio('View:', options=['Incremental Triangle', 'Cumulative Triangle', 'Age-to-Age',
                                      'LDFs', 'CDFs', 'Full Triangle', 'IBNR (with Case)', 'Case Reserves', 'Pure IBNR', 
                                      'Zeroized Pure IBNR', 'All'],
                    horizontal=True, key='view')
    st.write("<br>", unsafe_allow_html=True)

    if gross_net == 'Gross':
        amount = 'GROSS AMOUNT'
    elif gross_net == 'Net':
        amount = 'NET AMOUNT'

    # EXTRACT TRIANGLE BASED ON COB AND ADDITIONAL SEGMENTATION WHERE APPLICABLE
    if segment != 'No Segmentation':
        triangle = triangles[amount][(triangles[amount]['MAIN CLASS'] == cob) & (triangles[amount]['ADDITIONAL SEGMENTATION'] == segment)].grain(t_grain)
        if case_data is not None:
            os_diagonal = os_triangle[amount][(os_triangle[amount]['MAIN CLASS'] == cob) & (os_triangle[amount]['ADDITIONAL SEGMENTATION'] == segment)].grain(t_grain)
            os_res = os_diagonal.latest_diagonal
    elif segment == 'No Segmentation' and len(segments) > 1:
        triangle = triangles[amount][(triangles[amount]['MAIN CLASS'] == cob)].grain(t_grain).sum()
        if case_data is not None:
            os_diagonal = os_triangle[amount][(os_triangle[amount]['MAIN CLASS'] == cob)].grain(t_grain).sum()
            os_res = os_diagonal.latest_diagonal
    else:
        triangle = triangles[amount][(triangles[amount]['MAIN CLASS'] == cob)].grain(t_grain)
        if case_data is not None:
            os_diagonal = os_triangle[amount][(os_triangle[amount]['MAIN CLASS'] == cob)].grain(t_grain)
            os_res = os_diagonal.latest_diagonal
    
    dev_tri = cl.Chainladder().fit(triangle)

    incremental_triangle = triangle
    cumulative_triangle = triangle.incr_to_cum()
    age_to_age_factors = cumulative_triangle.age_to_age
    loss_development_factors = dev_tri.ldf_
    cumulative_factors = dev_tri.cdf_
    full_cumulative_triangle = dev_tri.full_triangle_.incr_to_cum()
    ibnr_with_case = dev_tri.ibnr_
    try:
        outstanding_diagonal = os_res
        pure_ibnr_df = pure_ibnr(dev_tri.ibnr_, os_res)[0]
        zeroized_ibnr_df = pure_ibnr(dev_tri.ibnr_, os_res)[1]
    except Exception:
        pass

    download_files = {
        "Incremental Triangle": incremental_triangle,
        "Cumulative Triangle": cumulative_triangle,
        "Age to Age Factors": age_to_age_factors,
        "LDFs": loss_development_factors,
        "CDFs": cumulative_factors,
        "Full Triangle": full_cumulative_triangle,
        "IBNR with Case": ibnr_with_case,
        }
    
    try:
        other_files = {
            "OS at valuation": outstanding_diagonal,
            "Pure IBNR": pure_ibnr_df,
            "Zeroized IBNR": zeroized_ibnr_df,
            }
    except Exception:
        pass
    
    for k, v in download_files.items():
        dff = v.to_frame()
        csv_file = convert_df(dff)
        download = st.sidebar.download_button(label= f"Download {k}",
                                              data=csv_file,
                                              file_name= f"{cob} ({t_grain}) - {k}.csv",
                                              mime="text/csv"
                                            )
        
    try:
        for k, v in other_files.items():
            if isinstance(v, pd.DataFrame):
                dff = v
                csv_file = convert_df(dff)
                download = st.sidebar.download_button(label= f"Download {k}",
                                                    data=csv_file,
                                                    file_name= f"{cob} ({t_grain}) - {k}.csv",
                                                    mime="text/csv"
                                                    )
            else:
                dff = v.to_frame()
                csv_file = convert_df(dff)
                download = st.sidebar.download_button(label= f"Download {k}",
                                                    data=csv_file,
                                                    file_name= f"{cob} ({t_grain}) - {k}.csv",
                                                    mime="text/csv"
                                            )
    except Exception:
        pass


    # DISPLAY TRIANGLES BASED ON SELECTED VIEW
    if view == 'Incremental Triangle':
        st.markdown(f"##### **Incremental Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(incremental_triangle)

    elif view == 'Cumulative Triangle':
        st.markdown(f"##### **Cumulative Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(cumulative_triangle)

    elif view == 'Age-to-Age':
        st.markdown(f"##### **Age-to-Age Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(age_to_age_factors)

    elif view == 'LDFs':
        st.markdown(f"##### **Loss Development Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(loss_development_factors)

    elif view == 'CDFs':
        st.markdown(f"##### **Cumulative Development Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(cumulative_factors)

    elif view == 'Full Triangle':
        st.markdown(f"##### **Full Projected-to-Ultimate Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(full_cumulative_triangle)

    elif view == 'IBNR (with Case)':
        st.markdown(f"##### **IBNR & Case Reserves**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(ibnr_with_case)

    elif view == 'Case Reserves':
        try:
            st.markdown(f"##### **Case Reserves at Reporting Date**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.write(outstanding_diagonal)
        except Exception:
            st.write("Check uploaded case reserves file")

    elif view == 'Pure IBNR':
        try:
            st.markdown(f"##### **Pure IBNR**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.dataframe(pure_ibnr_df, width=200, height=450, column_config={'Pure IBNR': st.column_config.NumberColumn('Pure IBNR', format='%d')})
        except Exception:
            st.write('Error Occured in Pure IBNR computation. Check uploaded files. Try to check if OS Date in Case Reserves File is appropriate')

    elif view == 'Zeroized Pure IBNR':
        try:
            st.markdown(f"##### **Zeroized Pure IBNR**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.dataframe(zeroized_ibnr_df, width=200, height=450, column_config={'Zeroized Pure IBNR': st.column_config.NumberColumn('Zeroized Pure IBNR', format='%d')})
        except Exception:
            st.write('Error Occured in Zeroized IBNR computation. Check uploaded files. Try to check if OS Date in Case Reserves File is appropriate')

    elif view == 'All':
        st.markdown(f"##### **Incremental Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(incremental_triangle)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **Cumulative Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(cumulative_triangle)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **Age-to-Age Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(age_to_age_factors)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **Loss Development Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(loss_development_factors)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **Cumulative Development Factors**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(cumulative_factors)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **Full Projected-to-Ultimate Triangle**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(full_cumulative_triangle)
        st.write("<br><br>", unsafe_allow_html=True)

        st.markdown(f"##### **IBNR & Case Reserves**")
        st.markdown(f'{gross_net} {cob} &mdash;{segment}')
        st.write(ibnr_with_case)
        st.write("<br><br>", unsafe_allow_html=True)

        try:
            st.markdown(f"##### **Case Reserves at Reporting Date**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.write(outstanding_diagonal)
            st.write("<br><br>", unsafe_allow_html=True)
        except Exception:
            st.write("Check uploaded case reserves file")

        try:
            st.markdown(f"##### **Pure IBNR**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.dataframe(pure_ibnr_df, width=200, height=450, column_config={'Pure IBNR': st.column_config.NumberColumn('Pure IBNR', format='%d')})
            st.write("<br>", unsafe_allow_html=True)
        except Exception:
            st.write('Error Occured in Pure IBNR computation. Check uploaded files. Also try to check if OS Date in Case Reserves File is appropriate')

        try:
            st.markdown(f"##### **Zeroized Pure IBNR**")
            st.markdown(f'{gross_net} {cob} &mdash;{segment}')
            st.dataframe(zeroized_ibnr_df, width=200, height=450, column_config={'Zeroized Pure IBNR': st.column_config.NumberColumn('Zeroized Pure IBNR', format='%d')})
            st.write("<br>", unsafe_allow_html=True)
        except Exception:
            st.write('Error Occured in Zeroized IBNR computation. Check uploaded files. Also try to check if OS Date in Case Reserves File is appropriate')
