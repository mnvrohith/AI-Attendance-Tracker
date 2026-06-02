import streamlit as st  

import streamlit as st


def header_home():

    logo_url = "https://i.ibb.co/CsVJ3xzm/logo.png"
    
    st.markdown(f"""
    <div style="
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    padding:30px 20px;
    margin:20px 0 35px 0;
    border-radius:20px;
    background:linear-gradient(
        135deg,
        rgba(255,255,255,0.08),
        rgba(255,255,255,0.03)
    );
    border:1px solid rgba(255,255,255,0.12);
    backdrop-filter:blur(10px);
   ">

    <img src="{logo_url}"
         style="
            height:110px;
            margin-bottom:15px;
            border-radius:45px;
            filter:drop-shadow(0px 4px 12px rgba(0,0,0,0.3));
         " />

    <h1 style="
        margin:0;
        text-align:center;
        color:#E0E3FF;
        font-size:42px;
        font-weight:800;
        letter-spacing:1px;
        line-height:1.1;
    ">
        AI Attendance Tracker
    </h1>

    <p style="
        margin-top:12px;
        color:rgba(255,255,255,0.75);
        font-size:16px;
        text-align:center;
        max-width:500px;
    ">
       Mark attendance seamlessly using AI-driven Face and Voice Recognition.
    </p>

    </div>
""", unsafe_allow_html=True)


def header_dashboard():

    logo_url = "https://i.ibb.co/CsVJ3xzm/logo.png"
    
    st.markdown(f"""
        <div style="
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    padding:30px 20px;
    margin:20px 0 35px 0;
    border-radius:20px;
    background:linear-gradient(
        135deg,
        rgba(255,255,255,0.08),
        rgba(255,255,255,0.03)
    );
    border:1px solid rgba(255,255,255,0.12);
    backdrop-filter:blur(10px);
   ">

    <img src="{logo_url}"
         style="
            height:110px;
            margin-bottom:15px;
            border-radius:45px;
            filter:drop-shadow(0px 4px 12px rgba(0,0,0,0.3));
         " />

 


    </div> 
                
                """, unsafe_allow_html=True)