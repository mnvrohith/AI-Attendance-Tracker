import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    if "student_page" not in st.session_state:
        st.session_state.student_page = "dashboard"
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn'):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data 
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button('Enroll in Subject', type='primary', width='stretch'):
            enroll_dialog()


    st.divider()
    if st.button(
        "Attendance Simulator",
        type="secondary",
        icon=":material/calculate:",
        width="stretch"
    ):
        st.session_state.student_page = "simulator"
        st.rerun()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    # Show simulator page when selected
    if st.session_state.student_page == "simulator":
        attendance_simulator_page(subjects, stats_map)
        footer_dashboard()
        return   
    
    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button():
                if st.button("Unenroll from this course", type='tertiary', width='stretch', icon=':material/delete_forever:',key=f"unenroll_{sub['subject_id']}"):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f'Unenrolled from {sub["name"]} successfully!')
                    st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                    ('📊', 'Attendance', f"{(stats['attended']/stats['total']*100) if stats['total']>0 else 0:.2f}%")
                ],
                footer_callback=unenroll_button
            )

    

def attendance_simulator_page(subjects, stats_map):
    c1, c2 = st.columns([3, 1], vertical_alignment="center")

    with c1:
        st.title("Attendance Simulator")

    with c2:
        if st.button("← Back to Dashboard", width="stretch"):
            st.session_state.student_page = "dashboard"
            st.rerun()

    attendance_simulator(subjects, stats_map)
def student_screen():


    style_background_dashboard()
    style_base_layout()


    if "student_data" in st.session_state:
        student_dashboard()
        return
    
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn'):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()
    
    show_registration = False
    photo_source = st.camera_input("Position your face in the center")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning..'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not found!')
            elif num_faces >1:
                st.warning('Multiple faces found')
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id']==student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f'Welcome Back {student["name"]}')
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! You might be a new student!')
                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your for voice only attendance")


            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings= get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture your facial features for registration')

                else:
                    st.warning('Please enter your name!')

       
        
    footer_dashboard()


import math

def attendance_simulator(subjects, stats_map):

    st.divider()
    st.caption(
        "Explore how your future attendance may affect "
        "your overall attendance percentage."
    )

    if not subjects:
        st.info("Enroll in a subject to use the attendance simulator.")
        return

    # Create a mapping of subject IDs to subject details
    subject_map = {
        str(node['subjects']['subject_id']): node['subjects']
        for node in subjects
    }

    selected_sid = st.selectbox(
        "Select Subject",
        options=list(subject_map.keys()),
        format_func=lambda sid: (
            f"{subject_map[sid]['name']} "
            f"({subject_map[sid]['subject_code']})"
        ),
        key="simulator_subject"
    )

    selected_stats = stats_map.get(
        selected_sid,
        stats_map.get(subject_map[selected_sid]['subject_id'],
                      {"total": 0, "attended": 0})
    )

    total_classes = selected_stats['total']
    attended_classes = selected_stats['attended']

    current_percentage = (
        attended_classes / total_classes * 100
        if total_classes > 0 else 0
    )

    st.divider()

    st.subheader("Your Current Attendance")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Classes", total_classes)
    c2.metric("Classes Attended", attended_classes)
    c3.metric("Current Attendance", f"{current_percentage:.2f}%")

    st.progress(min(current_percentage / 100, 1.0))
    st.subheader("Classes Required to Reach 75%")
    
    if current_percentage >= 75:
        st.success(
            "You have already achieved the required 75% attendance."
        )
    else:
        if total_classes == 0:
            required_classes = 1
        else:    
            required_classes = math.ceil(
                (0.75 * total_classes - attended_classes) / 0.25
            )

        st.info(
            f"You need to attend the next **{required_classes} "
            f"consecutive classes** without missing any to reach 75%."
        )

        if required_classes > upcoming_classes:
            st.caption(
                f"You need to attend all {int(upcoming_classes)} "
                f"simulated upcoming classes and continue attending "
                f"{required_classes - int(upcoming_classes)} more classes."
            )
    st.divider()

    st.subheader("Simulate Future Attendance")

    upcoming_classes = st.number_input(
        "Number of upcoming classes",
        min_value=1,
        max_value=500,
        value=10,
        step=1,
        key="sim_upcoming"
    )

    planned_attendance = st.slider(
        "How many upcoming classes will you attend?",
        min_value=0,
        max_value=int(upcoming_classes),
        value=int(upcoming_classes),
        step=1,
        key="sim_attended"
    )

    # Calculate projected attendance
    future_total = total_classes + int(upcoming_classes)
    future_attended = attended_classes + planned_attendance

    projected_percentage = (
        future_attended / future_total * 100
        if future_total > 0 else 0
    )

    st.divider()

    st.subheader("Your Projected Attendance")

    c1, c2 = st.columns(2)

    c1.metric(
        "Projected Attendance",
        f"{projected_percentage:.2f}%",
        delta=f"{projected_percentage - current_percentage:+.2f}%"
    )

    c2.metric(
        "Projected Classes Attended",
        f"{future_attended}/{future_total}"
    )

    st.progress(min(projected_percentage / 100, 1.0))

    if projected_percentage >= 75:
        st.success("You will maintain the required 75% attendance!")
    else:
        st.warning(
            "Your projected attendance will be below 75%. "
            "You need to attend more classes."
        )

    st.divider()

    
