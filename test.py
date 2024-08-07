import streamlit as st
import pandas as pd
import mysql.connector
import hashlib
from streamlit_extras.switch_page_button import switch_page
import st_pages as stp
from dotenv import load_dotenv
import os
load_dotenv()
# Function to create a connection to the database
def create_connection():
    return mysql.connector.connect(
        host=os.getenv('DATABASE_HOST'),
        user=os.getenv('DATABASE_USER'),
        password=os.getenv('DATABASE_PASSWORD'),
        database=os.getenv('DATABASE_NAME')
    )

# Function to create necessary tables
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS teachers
                      (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, password VARCHAR(255))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS students
                      (id INT AUTO_INCREMENT PRIMARY KEY, roll_number VARCHAR(255), name VARCHAR(255), dob DATE, marks INT)''')
    conn.commit()
    cursor.close()
    conn.close()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a new user
def create_user(username, password):
    hashed_password = hash_password(password)
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO teachers (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        st.success("Account Created Successfully")
        st.info("Go to Login Menu to login")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    cursor.close()
    conn.close()

# Function to authenticate teacher
def authenticate_teacher(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teachers WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.fetchall()  # Ensure all results are fetched
    cursor.close()
    conn.close()

    if user:
        stored_password = user[2]  # Password is the third column (0-indexed)
        hashed_password = hash_password(password)
        if stored_password == hashed_password:
            return "Success"
        else:
            return "Incorrect password"
    else:
        return "Username not found"

# Function to view result
def view_result(roll_number, dob):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE roll_number = %s AND dob = %s', (roll_number, dob))
    result = cursor.fetchone()
    cursor.fetchall()  # Ensure all results are fetched
    cursor.close()
    conn.close()
    if result:
        st.write("Name: ", result[2])
        st.write("Date of Birth: ", result[3])
        st.write("Marks: ", result[4])
    else:
        st.error("No record found")

# Main function to run the app
def main():
    stp.hide_pages(["manager","test"])
    st.title("Student Results Management System")
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'rerun' not in st.session_state:
        st.session_state.rerun = False
    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        roll_number = st.text_input("Enter Roll Number")
        dob = st.text_input("Enter Date of Birth (YYYY-MM-DD)")
        if st.button("View Result"):
            view_result(roll_number, dob)
    elif choice == "Login":
        st.subheader("Teacher Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            login_result = authenticate_teacher(username, password)
            if login_result == "Success":
                st.success(f"Logged In as {username}")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.rerun = True
                switch_page('manager')
            else:
                st.error(login_result)
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            if new_user != "" and new_password != "" :
                create_user(new_user, new_password)
            else :
                st.error("All fields are required !!!")

    if st.session_state.logged_in:
        st.sidebar.subheader(f"Welcome, {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("Logged out successfully")
            st.session_state.rerun = True
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)

    # if st.session_state.rerun:
    #     st.session_state.rerun = False
    #     st.rerun()

if __name__ == '__main__':
    create_tables()
    main()