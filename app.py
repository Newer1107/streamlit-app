import streamlit as st
import pandas as pd
import mysql.connector
import hashlib
import logging

logging.basicConfig(level=logging.DEBUG)

# MySQL Database setup
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='rooor',
        database='student_results'
    )

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
        add_student(new_roll_number, new_name, new_dob, new_marks)
    
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
        
# Main function to run the app
def main():
    st.title("Student Results Management System")
    
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    
    menu = ["Home", "Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        # Student section to view results
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
                st.success("Logged In as {}".format(username))
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error(login_result)
    
    if st.session_state.logged_in:
        st.sidebar.subheader("Welcome, {}".format(st.session_state.username))
        task = st.sidebar.selectbox("Task", ["Upload Data", "Manage Data"])

        if task == "Upload Data":
            upload_data()
        elif task == "Manage Data":
            manage_data()
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.success("Logged out successfully")
    
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            create_user(new_user, new_password)
            st.success("Account Created Successfully")
            st.info("Go to Login Menu to login")

if __name__ == '__main__':
    create_tables()
    main()
