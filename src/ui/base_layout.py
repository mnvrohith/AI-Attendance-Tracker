import streamlit as st


def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #EEEEEE !important;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:#FFFFFF !important;
                    padding:2.5rem !important;
                    border-radius: 5rem !important;
                    }
        </style>

                """
            ,unsafe_allow_html=True)


def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #EEEEEE !important;
                }

        </style>

                """
            ,unsafe_allow_html=True)




def style_base_layout():

    st.markdown("""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');


            #MainMenu, footer, header {
                visibility: hidden;
            }

            .block-container {
                padding-top:1.5rem !important;
            }

            h1 {
                font-family: 'Poppins', sans-serif !important;
                color: #1F6F5F !important;
                font-size: 3.5rem !important;
                line-height:1.1 !important;
                margin-bottom:0rem !important;
            }


            h2 {
                font-family: 'Poppins', sans-serif !important;
                color: #1F6F5F !important;
                font-size: 2rem !important;
                line-height:0.9 !important;
                margin-bottom:0rem !important;
            }

            h3, h4, p {
                font-family: 'Inter', sans-serif !important;
                color: #2D3748 !important;
            }


            button{
                border-radius: 1.5rem !important;
                background-color: #2FA084 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="secondary"]{
                border-radius: 1.5rem !important;
                background-color: #6FCF97 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="tertiary"]{
                border-radius: 1.5rem !important;
                background-color: #1F6F5F !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button:hover{
                transform :scale(1.05)
            }

        </style>

                """
            ,unsafe_allow_html=True)