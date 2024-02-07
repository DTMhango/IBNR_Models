import streamlit as st
from streamlit_extras.app_logo import add_logo
from data_validation import decode_image

st.set_page_config(layout='wide', page_title='Gralix Actuarial Reserving Interface', page_icon='Gralix Circle.ico')

for k, v in st.session_state.items():
    st.session_state[k] = v


def logo():
    add_logo("rsz_gralix2.png", height=150)

logo()

tab1, tab2, tab3 = st.tabs(['Reserving Interface', 'Who is this for?', 'Gralix Data Team'])

with tab1:
    st.markdown('###### Introducing GARI - The Gralix Actuarial Reserving Interface')
    st.markdown('''The ARI is a web application designed to streamline the Actuarial reserving workflow by abstracting 
                away modelling complexity. By harnessing the computational power of Python in the backend, the ARI sets itself apart from 
                traditional spreadsheet applications like excel, offering unparalleled efficiency and accuracy in actuarial loss reserving. 
                With just a few clicks and toggles you can clean data, analyze various scenarios, extract reports relevant to you and much more.''')
    st.markdown('###### **What does it do?**')
    st.markdown('''
                The Gralix ARI seamlessly integrates various actuarial reserving techniques including the Chain Ladder and Bornhuetter-Ferguson (BF) methodologies, 
                providing a robust framework for computing actuarial reserves. This dynamic tool ensures a precise and reliable estimation of reserves, empowering 
                insurance professionals to make informed decisions.''')
    st.markdown('''
                Underpinning the ARI is a sophisticated backend system that leverages Python's capabilities for data processing and complex computations. 
                This approach not only enhances the speed of the reserving process but also allows for scalability and adaptability to ever evolving industry 
                standards.''')
    st.markdown('###### **Design Considerations**')
    st.markdown('''
                The ARI's design philosophy centers around "simplicity." Unlike traditional actuarial software, everything from installation to usage
                has been designed to be as straightforward as possible. The user-friendly interface simplifies the actuarial reserving workflow, 
                enabling both actuaries and non-actuaries to navigate the application effortlessly. Users with basic knowledge of actuarial reserving 
                can easily interpret inputs and outputs, while those with more advanced expertise can customize the application to meet their specific 
                analytical needs. The ARI is not just a tool; it's a versatile platform that caters to a diverse range of users within the actuarial and 
                insurance communities.
             ''')
    
with tab2:
    st.markdown('###### **For Actuaries and More**')
    st.markdown('''
                The Gralix ARI caters to a broad audience, encompassing both seasoned actuaries and individuals new to the field. 
                Actuaries benefit from the application's advanced features, allowing them to delve into the intricacies of the reserving methodologies 
                and refine outputs according to their specialized requirements.''')
    st.markdown('''
                Simultaneously, the ARI is tailored to meet the needs of non-actuaries seeking a user-friendly solution for actuarial reserving. 
                The intuitive interface guides users through the process, demystifying complex calculations and making the world of actuarial science accessible 
                to a wider audience.''')
    st.markdown('''
                Whether you're a seasoned actuary looking for a powerful tool to streamline your workflow or a professional from another discipline seeking a 
                straightforward solution for actuarial reserving, the Gralix ARI is your go-to platform. Embrace the simplicity, precision, and efficiency that 
                define the future of actuarial reserving with the Gralix ARI.
                ''')
    colA, colB = st.columns(2)

    with colA:
        st.image(decode_image('IMG_8311.jpg'))
    
    with colB:
        st.image(decode_image('IMG_1.png'))
    
with tab3:
    st.markdown('''##### **Meet the Team**''')
    st.markdown('''
                The Gralix data team comprises of key members committed to developing data driven and automated solutions for our clients.
                The team's philosophy is the basis for the ARI design philosophy - **simplified execution for complex problems**. 
                With a committment to delivering an exceptional end user experience, the Gralix data team aims to be your go-to provider for automated, 
                data-centric financial solutions.''')
    
    col1, col2, col3, col4 = st.columns(4)

    mulenga = decode_image('Mulenga_4.jpg')
    daniel = decode_image('Daniel_3.jpg')
    chipo = decode_image('Chipo.jpg')
    juma = decode_image('Juma.jpg')
    
    with col1:
        st.markdown('#### **Mulenga Mutati**')
        st.image(mulenga)
        st.caption('Chief Executive Officer')
    
    with col2:
        st.markdown('#### **Daniel Mhango**')
        st.image(daniel, use_column_width=True)
        st.caption('Senior Data Specialist')

    
    with col3:
        st.markdown('#### **Chipo Sichizya**')
        st.image(chipo)
        st.caption('Senior Actuarial Analyst')

    with col4:
        st.markdown('#### **Juma M\'soka**')
        st.image(juma)
        st.caption('Actuarial Analyst/Data Specialist')
