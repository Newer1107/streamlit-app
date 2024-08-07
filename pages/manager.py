import streamlit as st
import pandas as pd
import mysql.connector
import logging
from streamlit_extras.switch_page_button import switch_page
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

# Function to upload data
def upload_data():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            conn = create_connection()
            cursor = conn.cursor()
            data = pd.read_csv(uploaded_file)
            st.write("Uploaded Data Preview:")
            st.write(data)
            for index, row in data.iterrows():
                cursor.execute('INSERT INTO students (roll_number, name, dob, marks) VALUES (%s, %s, %s, %s)', 
                              (row['roll_number'], row['name'], row['dob'], row['marks']))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Data uploaded successfully")
        except Exception as e:
            st.error(f"Error uploading data: {e}")
            logging.error(f"Error uploading data: {e}")

# Function to manage data
def manage_data():
    st.subheader("Edit Database")
    
    # Viewing Data
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(data, columns=['ID', 'Roll Number', 'Name', 'Date of Birth', 'Marks'])
    st.write("Current Data in Database:")
    st.write(df)
    
    # Add Student
    st.subheader("Add Student")
    new_roll_number = st.text_input("New Student's Roll Number")
    new_name = st.text_input("New Student's Name")
    new_dob = st.text_input("New Student's Date of Birth (YYYY-MM-DD)")
    new_marks = st.text_input("New Student's Marks")
    
    if st.button("Add Student"):
        if new_roll_number != "" and new_name != "" and new_dob != "" and new_marks != "":
            add_student(new_roll_number, new_name, new_dob, new_marks)
        else:
            st.error("All fields are required")        
    
    # Updating Data
    st.write("Enter the details to update the database:")
    roll_number = st.text_input("Roll Number")
    name = st.text_input("Name")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    marks = st.text_input("Marks")
    
    if st.button("Update Database"):
        update_database(roll_number, name, dob, marks)
    
    # Deleting Data
    st.write("Enter the Roll Number of the student to delete:")
    del_roll_number = st.text_input("Roll Number to Delete")
    
    if st.button("Delete from Database"):
        delete_from_database(del_roll_number)

# Function to add a new student
def add_student(roll_number, name, dob, marks):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO students (roll_number, name, dob, marks) VALUES (%s, %s, %s, %s)',
                       (roll_number, name, dob, marks))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("New student added successfully")
    except Exception as e:
        st.error(f"Error adding new student: {e}")

# Function to update database
def update_database(roll_number, name, dob, marks):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE students SET name = %s, dob = %s, marks = %s WHERE roll_number = %s',
                       (name, dob, marks, roll_number))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Database updated successfully")
    except Exception as e:
        st.error(f"Error updating database: {e}")

# Function to delete from database
def delete_from_database(roll_number):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM students WHERE roll_number = %s', (roll_number,))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("Record deleted successfully")
    except Exception as e:
        st.error(f"Error deleting record: {e}")

def main():
    st.title("Database Management")
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.sidebar.subheader(f"Welcome, {st.session_state.username}!")
        task = st.sidebar.selectbox("Task", ["Upload Data", "Manage Data"])
        if task == "Upload Data":
            upload_data()
        elif task == "Manage Data":
            manage_data()
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("Logged out successfully")
            st.rerun()
    else:
        st.error("Please login from the main app")
        switch_page("test")
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
        

if __name__ == '__main__':
    main()
