from flask import Flask, render_template, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "knbvftyujnbvftyjnvcfghjn"

db_config = {
    "host" : "localhost",
    "user" : "root",
    "password" : "Lesjo@143",
    "database" : "student_management_db" 
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    if session["role"] == "teacher":
        # Join to get student names for teachers
        query = """
        SELECT m.*, s.student_name 
        FROM mark_list m 
        INNER JOIN student s ON m.student_id = s.student_id
        """
        cursor.execute(query)
    else:
        # Join to get student name for a specific student
        query = """
        SELECT m.*, s.student_name 
        FROM mark_list m 
        INNER JOIN student s ON m.student_id = s.student_id 
        WHERE m.student_id = %s
        """
        cursor.execute(query, (session['user_id'],))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("dashboard.html", data=data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"] 

        # Determine which table to query based on role
        table = "teacher" if role == "teacher" else "student"
        name_column = "teacher_name" if role == "teacher" else "student_name"

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = f"SELECT * FROM {table} WHERE {name_column} = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["role"] = role  
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")  # Create one unified login page

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        password_hash = generate_password_hash(password)

        table = "teacher" if role == "teacher" else "student"
        name = "teacher_name" if role == "teacher" else "student_name"

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = f"INSERT INTO {table} ({name}, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("login"))
    
    return render_template("/register.html")

@app.route("/edit/<int:student_id>", methods=["GET"])  # GET for showing the form
def edit_form(student_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT tamil, english, maths, grade FROM mark_list WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    current_marks = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # If no marks found, create an empty tuple to prevent template errors
    if not current_marks:
        current_marks = ('', '', '', '')
    
    return render_template("edit.html", 
                         student_id=student_id, 
                         current_marks=current_marks)

@app.route("/edit", methods=["POST"])
def edit_update():  # Fixed function name (was edit_update but you had edit_update)
    student_id = request.form["student_id"]
    tamil = request.form["tamil"]
    english = request.form["english"]
    maths = request.form["maths"]
    grade = request.form["grade"]
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """UPDATE mark_list 
                SET tamil = %s, english = %s, maths = %s, grade = %s
                WHERE student_id = %s"""
    cursor.execute(query, (tamil, english, maths, grade, student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))
    


@app.route("/delete", methods=["POST"])
def delete():
    # Get student_id from form data instead of session
    student_id = request.form["student_id"]
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "DELETE FROM mark_list WHERE student_id = %s"
    cursor.execute(query, (student_id,))  # Note the comma to make it a tuple
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route('/logout')
def logout():
    session.clear() # Wipe the session data
    return redirect(url_for('home'))

    
if __name__ == "__main__":
    app.run(debug=True)