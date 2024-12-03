### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### app.py

from flask import Flask, render_template
import db  # Import the database module
from flask import request, redirect, url_for, session, flash


# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration for the SQLite database
app.config['DATABASE'] = 'data.db'


# Register teardown and database commands
app.teardown_appcontext(db.close_db)
app.cli.add_command(db.init_db)  # Register the CLI command

# Define the route for the home page
@app.route("/")
def home():
    return render_template("index.html")

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if db.verify_admin_user(username, password):
            session["admin_logged_in"] = True
            session["admin_username"] = username  # Store the username in the session
            print(f"Logged in as: {username}")
            return redirect(url_for("admin_dashboard"))
        else:
            print("Login failed.")
            flash("Invalid credentials, please try again.")
    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)  # Remove the username
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/admin-dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        print("Admin not logged in. Redirecting to login page.")
        return redirect(url_for("admin_login"))
    print("Admin logged in. Rendering admin_dashboard.html.")
    return render_template("admin_dashboard.html")


@app.context_processor
def inject_user_status():
    """Inject login status and username into all templates."""
    is_logged_in = "admin_logged_in" in session and session["admin_logged_in"]
    username = session.get("admin_username", "Unknown User") if is_logged_in else None
    return {"is_logged_in": is_logged_in, "username": username}

