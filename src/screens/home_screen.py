import streamlit as st
from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():

    style_base_layout()
    style_background_home()
    header_home()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="text-align:center; padding:20px;">
            <h2 style="color:#1F6F5F;">🎓 Student</h2>
            <p style="color:#2D3748;">
                Enroll in subjects, track your attendance.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.image("https://i.ibb.co/qLZK2njD/student.png", width=180)

        if st.button(
            "Enter Student Portal",
            key="student_btn",
            type="primary",
            icon=":material/school:",
            use_container_width=True
        ):
            st.session_state["login_type"] = "student"
            st.rerun()

    with col2:
        st.markdown("""
        <div style="text-align:center; padding:20px;">
            <h2 style="color:#1F6F5F;">👨‍🏫 Teacher</h2>
            <p style="color:#2D3748;">
                Manage subjects, take attendance using AI.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.image("https://i.ibb.co/wFLfKyxZ/teacher.png", width=180)

        if st.button(
            "Enter Teacher Portal",
            key="teacher_btn",
            type="primary",
            icon=":material/co_present:",
            use_container_width=True
        ):
             st.session_state["login_type"] = "teacher"
             st.rerun()

    footer_home()