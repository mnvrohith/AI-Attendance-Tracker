import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_subject_students,
    get_subject_attendance,
)
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendance
from src.components.dialog_attendance_results import attendance_result_dialog
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendance import voice_attendance_dialog
def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3, tab4 = st.columns(4)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    with tab4:
        type4 = "primary" if st.session_state.current_teacher_tab == 'Attendance Analysis' else "tertiary"
        if st.button('Attendance Analysis', type=type4, width='stretch', icon=':material/analytics:'):
            st.session_state.current_teacher_tab = 'Attendance Analysis'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
    if st.session_state.current_teacher_tab == "Attendance Analysis":
        teacher_tab_attendance_analysis()
    


    footer_dashboard()

def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')


    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return
    
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4 ]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()


    with c2:
        
        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)


                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id',selected_subject_id ).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log  = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present= len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)











def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)


    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:

        for sub in subjects:

            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            def share_btn(sub=sub):
                if st.button(
                    f"Share Code: {sub['name']}",
                    key=f"share_{sub['subject_code']}",
                    icon=":material/share:"
                ):
                    share_subject_dialog(
                        sub['name'],
                        sub['subject_code']
                    )

                st.space()

            subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=stats,
                    footer_callback=share_btn
            )

    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")



import pandas as pd
import streamlit as st
from datetime import datetime


def teacher_tab_attendance_records():

    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data["teacher_id"]

    # Fetch teacher subjects
    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info("No subjects available.")
        return

    # Subject selection
    selected_subject = st.selectbox(
        "Select Subject",
        subjects,
        format_func=lambda s: (
            f"{s['name']} ({s['subject_code']}) - {s['section']}"
        ),
        key="attendance_register_subject"
    )

    subject_id = selected_subject["subject_id"]

    # Fetch enrolled students and attendance logs
    enrolled = get_subject_students(subject_id)
    logs = get_subject_attendance(subject_id)

    if not enrolled:
        st.warning("No students enrolled in this subject.")
        return

    # Student information
    students = []

    for row in enrolled:
        student = row.get("students") or {}

        students.append({
            "Student ID": row["student_id"],
            "Student Name": student.get("name", "Unknown")
        })

    students_df = pd.DataFrame(students)

    total_students = len(students_df)

    # Attendance sessions
    sessions = sorted(
        set(
            r["timestamp"]
            for r in logs
            if r.get("timestamp")
        )
    )

    total_sessions = len(sessions)

    # --------------------------------
    # ATTENDANCE OVERVIEW
    # --------------------------------

    st.subheader("Attendance Overview")

    if total_sessions > 0:

        # Calculate attendance for each student
        student_attendance = {}

        for student_id in students_df["Student ID"]:

            attended = sum(
                1
                for log in logs
                if log["student_id"] == student_id
                and log.get("is_present")
            )

            student_attendance[student_id] = (
                attended / total_sessions * 100
            )

        average_attendance = (
            sum(student_attendance.values()) / total_students
            if total_students > 0 else 0
        )

    else:
        student_attendance = {
            student_id: 0
            for student_id in students_df["Student ID"]
        }
        average_attendance = 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Students", total_students)
    col2.metric("Classes Conducted", total_sessions)
    col3.metric(
        "Average Attendance",
        f"{average_attendance:.2f}%"
    )

    # --------------------------------
    # ATTENDANCE RECORD
    # --------------------------------

    st.divider()
    st.subheader("Attendance Record")

    # Create attendance register
    register = students_df.set_index(
        ["Student ID", "Student Name"]
    )

    for session in sessions:

        session_logs = {
            r["student_id"]: r["is_present"]
            for r in logs
            if r["timestamp"] == session
        }

        register[session] = [
            session_logs.get(student_id, False)
            for student_id in register.index.get_level_values(
                "Student ID"
            )
        ]

    # Attendance percentage
    if sessions:
        register["Attendance %"] = (
            register[sessions].sum(axis=1) / total_sessions * 100
        ).round(2)
    else:
        register["Attendance %"] = 0.0

    # Convert True/False to P/A
    display_register = register.copy()

    for session in sessions:
        display_register[session] = display_register[session].map(
            lambda x: "P" if x else "A"
        )

    # Format session column labels
    session_labels = {
        session: datetime.fromisoformat(session).astimezone().strftime(
            "%d-%b %I:%M %p"
        )
        for session in sessions
    }

    display_register = display_register.rename(
        columns=session_labels
    )

    display_register = display_register.reset_index()

    st.dataframe(
        display_register,
        width="stretch",
        hide_index=True
    )

    if not sessions:
        st.info(
            "Attendance categories will be available "
            "after the first attendance session."
        )
        return



    # --------------------------------
    # EDIT ATTENDANCE
    # --------------------------------

    st.divider()
    st.subheader("Edit Attendance")

    if sessions:

        selected_session = st.selectbox(
            "Select Class Session",
            sessions,
            format_func=lambda session: (
                datetime.fromisoformat(session)
                .astimezone()
                .strftime("%d-%b-%Y %I:%M %p")
            ),
            key="edit_attendance_session"
        )

        selected_student_id = st.selectbox(
            "Select Student",
            list(students_df["Student ID"]),
            format_func=lambda sid: students_df.loc[
                students_df["Student ID"] == sid,
                "Student Name"
            ].iloc[0],
            key="edit_attendance_student"
        )

        # Get current attendance status
        current_log = next(
            (
                log for log in logs
                if log["student_id"] == selected_student_id
                and log["timestamp"] == selected_session
            ),
            None
        )

        current_status = (
            current_log["is_present"]
            if current_log else False
        )

        new_status = st.radio(
            "Attendance Status",
            ["Present", "Absent"],
            index=0 if current_status else 1,
            horizontal=True,
            key="edit_attendance_status"
        )

        if st.button(
            "Save Attendance Changes",
            type="primary",
            key="save_attendance_changes"
        ):

            updated_status = new_status == "Present"

            try:

                if current_log:

                    # Update existing attendance record
                    response = (
                        supabase.table("attendance_logs")
                        .update({
                            "is_present": updated_status
                        })
                        .eq("student_id", selected_student_id)
                        .eq("subject_id", subject_id)
                        .eq("timestamp", selected_session)
                        .select()
                        .execute()
                    )

                else:

                    # Insert record if it does not exist
                    response = (
                        supabase.table("attendance_logs")
                        .insert({
                            "student_id": selected_student_id,
                            "subject_id": subject_id,
                            "timestamp": selected_session,
                            "is_present": updated_status
                        })
                        .execute()
                    )

                st.toast("Attendance updated successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Unable to update attendance: {e}")

    # --------------------------------
    # ATTENDANCE CATEGORIES
    # --------------------------------

    st.divider()
    st.subheader("Attendance Categories")

    category = st.selectbox(
        "Select Attendance Category",
        [
            "75% and Above",
            "50% - 74%",
            "25% - 49%",
            "Below 25%"
        ],
        key="records_attendance_category"
    )

    categorized_students = []

    for student_id, percentage in student_attendance.items():

        student_name = students_df.loc[
            students_df["Student ID"] == student_id,
            "Student Name"
        ].iloc[0]

        if category == "75% and Above" and percentage >= 75:
            categorized_students.append({
                "Student Name": student_name,
                "Attendance Percentage": round(percentage, 2)
            })

        elif category == "50% - 74%" and 50 <= percentage < 75:
            categorized_students.append({
                "Student Name": student_name,
                "Attendance Percentage": round(percentage, 2)
            })

        elif category == "25% - 49%" and 25 <= percentage < 50:
            categorized_students.append({
                "Student Name": student_name,
                "Attendance Percentage": round(percentage, 2)
            })

        elif category == "Below 25%" and percentage < 25:
            categorized_students.append({
                "Student Name": student_name,
                "Attendance Percentage": round(percentage, 2)
            })

    if categorized_students:

        category_df = pd.DataFrame(categorized_students)

        st.dataframe(
            category_df,
            width="stretch",
            hide_index=True
        )

    else:
        st.success("No students found in this category.")


   

def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()


    
# def teacher_tab_attendance_analysis():

#     st.header("Attendance Analysis")

#     teacher_id = st.session_state.teacher_data["teacher_id"]

#     subjects = get_teacher_subjects(teacher_id)

#     if not subjects:
#         st.info("No subjects available.")
#         return

#     selected_subject = st.selectbox(
#         "Select Subject",
#         subjects,
#         format_func=lambda s: (
#             f"{s['name']} ({s['subject_code']}) - {s['section']}"
#         ),
#         key="analysis_subject"
#     )

#     subject_id = selected_subject["subject_id"]

 
#     enrolled_students = get_subject_students(subject_id)
#     attendance_logs = get_subject_attendance(subject_id)

#     if not enrolled_students:
#         st.info("No students enrolled in this subject.")
#         return

#     # Student information
#     students = {}

#     for row in enrolled_students:
#         student = row.get("students")

#         if student:
#             student_id = row["student_id"]

#             students[student_id] = {
#                 "name": student["name"],
#                 "present": 0,
#                 "percentage": 0
#             }

#     total_students = len(students)

#     if total_students == 0:
#         st.info("No student information available.")
#         return

 
#     sessions = sorted(
#         set(log["timestamp"] for log in attendance_logs)
#     )

#     if not sessions:
#         st.info("No attendance sessions recorded yet.")
#         return

   
#     attendance_matrix = {}

#     for student_id in students:
#         attendance_matrix[student_id] = {}

#         for session in sessions:
#             attendance_matrix[student_id][session] = 0

#     for log in attendance_logs:
#         student_id = log["student_id"]
#         session = log["timestamp"]

#         if student_id in attendance_matrix:
#             attendance_matrix[student_id][session] = (
#                 1 if log["is_present"] else 0
#             )

 
#     total_sessions = len(sessions)

#     for student_id in students:
#         present_count = sum(
#             attendance_matrix[student_id].values()
#         )

#         percentage = (
#             present_count / total_sessions * 100
#         )

#         students[student_id]["present"] = present_count
#         students[student_id]["percentage"] = percentage


#     st.subheader("Attendance Trend")

#     chart_mode = st.radio(
#         "View Attendance Trend",
#         ["Overall Class", "Individual Student"],
#         horizontal=True,
#         key="analysis_chart_mode"
#     )

#     # Overall class attendance per session
#     if chart_mode == "Overall Class":

#         class_percentages = []

#         for session in sessions:

#             present_count = sum(
#                 attendance_matrix[student_id][session]
#                 for student_id in students
#             )

#             percentage = (
#                 present_count / total_students * 100
#             )

#             class_percentages.append(percentage)

#         chart_data = pd.DataFrame({
#             "Session": range(1, total_sessions + 1),
#             "Attendance Percentage": class_percentages
#         })

#         st.line_chart(
#             chart_data.set_index("Session")
#         )

#     # Individual student attendance trend
#     else:

#         student_options = list(students.keys())

#         selected_student = st.selectbox(
#             "Select Student",
#             student_options,
#             format_func=lambda sid: students[sid]["name"],
#             key="analysis_student"
#         )

#         cumulative_percentages = []
#         present_count = 0

#         for session in sessions:

#             present_count += attendance_matrix[selected_student][session]

#             percentage = (
#                 present_count /
#                 (sessions.index(session) + 1) * 100
#             )

#             cumulative_percentages.append(percentage)

#         chart_data = pd.DataFrame({
#             "Session": range(1, total_sessions + 1),
#             "Attendance Percentage": cumulative_percentages
#         })

#         st.line_chart(
#             chart_data.set_index("Session")
#         )

  
#     st.divider()

#     st.subheader("Attendance Categories")

#     category = st.selectbox(
#         "Select Attendance Category",
#         [
#             "75% and Above",
#             "50% - 74%",
#             "25% - 49%",
#             "Below 25%"
#         ],
#         key="analysis_category"
#     )

#     # Categorize students
#     categorized_students = []

#     for student_id, student in students.items():

#         percentage = student["percentage"]

#         if category == "75% and Above" and percentage >= 75:
#             categorized_students.append(student)

#         elif category == "50% - 74%" and 50 <= percentage < 75:
#             categorized_students.append(student)

#         elif category == "25% - 49%" and 25 <= percentage < 50:
#             categorized_students.append(student)

#         elif category == "Below 25%" and percentage < 25:
#             categorized_students.append(student)

#     # Display student list
#     if categorized_students:

#         student_data = pd.DataFrame([
#             {
#                 "Student Name": student["name"],
#                 "Classes Attended": student["present"],
#                 "Attendance Percentage": round(
#                     student["percentage"], 2
#                 )
#             }
#             for student in categorized_students
#         ])

#         st.dataframe(
#             student_data,
#             use_container_width=True,
#             hide_index=True
#         )

#     else:
#         st.success("No students found in this category.")

import math
def teacher_tab_attendance_analysis():

    st.header("Attendance Analysis & Risk Assessment")

    st.caption(
        "Identify students who may be at risk of falling below "
        "the required 75% attendance threshold."
    )

    teacher_id = st.session_state.teacher_data["teacher_id"]

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.info("No subjects available.")
        return

    selected_subject = st.selectbox(
        "Select Subject",
        subjects,
        format_func=lambda s: (
            f"{s['name']} ({s['subject_code']}) - {s['section']}"
        ),
        key="analysis_subject"
    )

    subject_id = selected_subject["subject_id"]

    enrolled_students = get_subject_students(subject_id)
    attendance_logs = get_subject_attendance(subject_id)

    if not enrolled_students:
        st.info("No students enrolled in this subject.")
        return

    # Student information
    students = {}

    for row in enrolled_students:
        student = row.get("students")

        if student:
            student_id = row["student_id"]

            students[student_id] = {
                "name": student["name"],
                "present": 0,
                "percentage": 0
            }

    total_students = len(students)

    if total_students == 0:
        st.info("No student information available.")
        return

    # Get unique attendance sessions
    sessions = sorted(
        set(
            log["timestamp"]
            for log in attendance_logs
            if log.get("timestamp")
        )
    )

    if not sessions:
        st.info("No attendance sessions recorded yet.")
        return

    # Build attendance matrix
    attendance_matrix = {}

    for student_id in students:
        attendance_matrix[student_id] = {
            session: 0 for session in sessions
        }

    for log in attendance_logs:
        student_id = log["student_id"]
        session = log["timestamp"]

        if (
            student_id in attendance_matrix
            and session in attendance_matrix[student_id]
        ):
            attendance_matrix[student_id][session] = (
                1 if log["is_present"] else 0
            )

    # Calculate attendance percentages
    total_sessions = len(sessions)

    for student_id in students:

        attendance = [
            attendance_matrix[student_id][session]
            for session in sessions
        ]

        present_count = sum(attendance)

        percentage = (
            present_count / total_sessions * 100
        )

        students[student_id]["present"] = present_count
        students[student_id]["percentage"] = percentage

    # --------------------------------
    # ATTENDANCE RISK ASSESSMENT
    # --------------------------------

    risk_results = []

    for student_id, student in students.items():

        attendance = [
            attendance_matrix[student_id][session]
            for session in sessions
        ]

        current_percentage = student["percentage"]

        # Recent attendance trend
        if total_sessions >= 10:

            recent = attendance[-5:]
            previous = attendance[-10:-5]

            recent_percentage = sum(recent) / 5 * 100
            previous_percentage = sum(previous) / 5 * 100

            trend_difference = (
                recent_percentage - previous_percentage
            )

            if trend_difference <= -20:
                trend = "Declining"
            elif trend_difference >= 20:
                trend = "Improving"
            else:
                trend = "Stable"

        else:
            trend = "Insufficient Data"

        # Consecutive absences
        consecutive_absences = 0

        for status in reversed(attendance):
            if status == 0:
                consecutive_absences += 1
            else:
                break

        # Risk score
        risk_score = 0

        if current_percentage < 65:
            risk_score += 40
        elif current_percentage < 75:
            risk_score += 25

        if trend == "Declining":
            risk_score += 25
        elif trend == "Stable":
            risk_score += 10

        if consecutive_absences >= 3:
            risk_score += 35
        elif consecutive_absences >= 1:
            risk_score += 15

        # Risk classification
        if risk_score >= 60:
            risk_level = "High"
        elif risk_score >= 30:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Classes required to reach 75%
        if current_percentage >= 75:
            required_classes = 0
        else:
            required_classes = max(
                0,
                math.ceil(
                    (0.75 * total_sessions - student["present"]) / 0.25
                )
            )

        risk_results.append({
            "Student ID": student_id,
            "Student Name": student["name"],
            "Attendance (%)": round(current_percentage, 2),
            "Recent Trend": trend,
            "Consecutive Absences": consecutive_absences,
            "Classes to Attend": required_classes,
            "Risk Score": risk_score,
            "Risk Level": risk_level
        })

    # --------------------------------
    # RISK OVERVIEW
    # --------------------------------

    st.divider()
    st.subheader("Risk Overview")

    high_risk = sum(
        1 for s in risk_results if s["Risk Level"] == "High"
    )

    moderate_risk = sum(
        1 for s in risk_results if s["Risk Level"] == "Moderate"
    )

    low_risk = sum(
        1 for s in risk_results if s["Risk Level"] == "Low"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("High Risk", high_risk)
    col2.metric("Moderate Risk", moderate_risk)
    col3.metric("Low Risk", low_risk)

    # --------------------------------
    # STUDENT-WISE RISK ANALYSIS
    # --------------------------------

    st.divider()
    st.subheader("Student-wise Risk Analysis")

    risk_df = pd.DataFrame(risk_results)

    risk_df = risk_df.sort_values(
        by="Risk Score",
        ascending=False
    )

    st.dataframe(
        risk_df.drop(columns=["Student ID"]),
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------
    # INDIVIDUAL STUDENT RISK DETAILS
    # --------------------------------

    st.divider()
    st.subheader("Individual Student Risk Details")

    selected_student_id = st.selectbox(
        "Select Student",
        list(students.keys()),
        format_func=lambda sid: students[sid]["name"],
        key="risk_student"
    )

    selected_result = next(
        s for s in risk_results
        if s["Student ID"] == selected_student_id
    )

    st.metric(
        "Current Attendance",
        f"{selected_result['Attendance (%)']:.2f}%"
    )

    st.write(
        f"**Risk Level:** {selected_result['Risk Level']}"
    )

    st.write(
        f"**Recent Trend:** {selected_result['Recent Trend']}"
    )

    st.write(
        f"**Consecutive Absences:** "
        f"{selected_result['Consecutive Absences']}"
    )

    st.write(
        f"**Classes to attend to reach 75%:** "
        f"{selected_result['Classes to Attend']}"
    )

    if selected_result["Risk Level"] == "High":

        st.error(
            "Teacher Recommendation: Prioritize this student "
            "for attendance follow-up."
        )

    elif selected_result["Risk Level"] == "Moderate":

        st.warning(
            "Teacher Recommendation: Monitor this student's "
            "attendance in upcoming classes."
        )

    else:

        st.success(
            "Teacher Recommendation: Attendance is currently "
            "under control. Continue monitoring."
        )
