# AI Attendance Tracker

AI Attendance Tracker is a smart attendance management system that uses **Face Recognition** and **Voice Recognition** to automate student attendance. The platform provides dedicated portals for teachers and students, enabling efficient attendance tracking, subject management, and attendance monitoring through an intuitive web interface.

## Features

### Teacher Portal

* Teacher registration and login
* Create and manage subjects
* Enroll students into courses
* Mark attendance using AI-powered recognition
* View attendance statistics and records

### Student Portal

* Student registration and login
* Enroll in available subjects
* View attendance history
* Track attendance percentage
* Monitor attendance status

---

## Tech Stack

- **Streamlit** – Frontend framework used to build the web application interface.
- **Supabase** – Backend database used for storing users, subjects, attendance records, and embeddings.

### Face Recognition
- **Dlib Face Recognition Model** – Used for face detection and generation of 128-dimensional face embeddings.
- **Support Vector Machine (SVM)** – Used to classify and identify students based on facial embeddings.
- **Euclidean Distance Matching** – Used to verify face recognition results and reduce false positives.

### Voice Recognition
- **Resemblyzer VoiceEncoder** – Used to generate speaker embeddings from audio recordings.
- **Cosine Similarity Matching** – Used to identify speakers by comparing voice embeddings.
- **Librosa** – Used for audio loading, preprocessing, and speech segmentation.

### Utilities
- **NumPy** – Numerical computations and similarity calculations.
- **Pandas** – Data handling and attendance analytics.
- **Bcrypt** – Secure password hashing.
- **Pillow** – Image processing.
- **Segno** – QR code generation.

## Deployment

The application is deployed on **Streamlit Cloud**.

---
