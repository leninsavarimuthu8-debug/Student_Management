from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from flask import session 

app = Flask(__name__)
app.secret_key = "qwertyhgfdsxcvb"

db_config = {
    "host" : "localhost",
    "user" : "root",
    "password" : "Lesjo@143",
    "database" : "movies_db"
}

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # If they are logged in, show their movies
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # MODIFY THIS QUERY: Only select movies for the logged-in user!
    query = "SELECT id, title, director, year_of_relese, my_rating FROM movies WHERE user_id = %s"
    cursor.execute(query, (session['user_id'],)) # Use the user_id from the session
    all_movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", all_movies=all_movies)

@app.route("/add_movies", methods=["POST"])
def add_movies():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    new_movie = request.form.get("new_movie")
    new_director = request.form.get("new_director")
    year_of_relese = request.form.get("year_of_relese")
    rating = request.form.get("my_rating")
    
    # MODIFIED QUERY: Add the user_id to the INSERT
    query = "INSERT INTO movies (title, director, year_of_relese, my_rating, user_id) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (new_movie, new_director, year_of_relese, rating, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("home"))

@app.route("/edit_movie/<int:movie_id>", methods=["GET", "POST"])
def edit_movie(movie_id):
    if request.method == "POST":
        e_title = request.form.get("e_title")
        e_director = request.form.get("e_director")
        e_year_of_relese = request.form.get("e_year_of_relese")
        e_rating = request.form.get("e_rating")

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "UPDATE movies SET title = %s, director = %s, year_of_relese = %s, my_rating = %s WHERE id = %s"
        cursor.execute(query, (e_title, e_director, e_year_of_relese, e_rating, movie_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("home"))
    else:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT id, title, director, year_of_relese, my_rating FROM movies WHERE id = %s"
        cursor.execute(query, (movie_id,))
        movie_to_edit = cursor.fetchone()
        cursor.close()
        conn.close()
        # FIXED: Pass both the movie data AND the movie_id to the template
        return render_template("edit.html", movies=movie_to_edit, movie_id=movie_id)
    
@app.route("/delete_movie/<int:movie_id>")
def delete_movie(movie_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "DELETE FROM movies WHERE id = %s "
    cursor.execute(query, (movie_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("home"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password before storing it
        password_hash = generate_password_hash(password)
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Insert the new user into the database
        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (username, password_hash))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('login')) # Redirect to login page after registration
    
    # If it's a GET request, just show the registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True) # Use dictionary cursor to get columns by name
        # Find the user by their username
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone() # This will be one user record or None
        cursor.close()
        conn.close()
        
        # Check if user exists AND password is correct
        if user and check_password_hash(user['password_hash'], password):
            # Password is correct! Log the user in.
            session['user_id'] = user['id'] # Store user's ID in the session
            return redirect(url_for('home'))
        else:
            # Password was wrong or user doesn't exist
            return "Invalid username or password", 401
    
    # If it's a GET request, just show the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Wipe the session data
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)