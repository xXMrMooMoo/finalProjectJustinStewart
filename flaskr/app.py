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

        user_exists = db.get_admin_user(username)  # Check if the user exists
        if not user_exists:
            flash(f"Incorrect username: {username}", "danger")
        elif not db.verify_admin_user(username, password):
            flash(f"Incorrect password for username: {username}", "danger")
        else:
            session["admin_logged_in"] = True
            session["admin_username"] = username
            # Redirect to dashboard without flashing the welcome message here
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")


@app.route("/admin-logout")
def admin_logout():
    username = session.get("admin_username", "Unknown User")  # Get the username from the session
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash(f"User: {username} logged out.", "info")  # Pass a flash message
    return redirect(url_for("home"))  # Redirect to the index page


@app.route("/admin-dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        if "create_user" in request.form:
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if password != confirm_password:
                # Flash an error message if passwords don't match
                flash("Passwords do not match. Please try again.", "danger")
            else:
                # Try creating the user and flash success or error messages
                message = db.add_admin_user(username, password)
                if "already exists" in message:
                    flash(message, "danger")
                else:
                    flash(f"Admin user '{username}' created successfully.", "success")

        elif "delete_user" in request.form:
            username = request.form.get("username")
            message = db.delete_admin_user(username)
            flash(message, "info")

        elif "reinit_db" in request.form:
            message = db.reinitialize_database()
            flash(message, "warning")

    admin_users = db.list_admin_users()
    return render_template("admin_dashboard.html", admin_users=admin_users)



@app.context_processor
def inject_user_status():
    """Inject login status and username into all templates."""
    is_logged_in = session.get("admin_logged_in", False)
    username = session.get("admin_username") if is_logged_in else None
    return {"is_logged_in": is_logged_in, "username": username}


@app.route("/full-inventory")
def full_inventory():
    db_connection = db.get_db()
    cursor = db_connection.cursor()
    # Define tables with their custom display formats
    tables = [
        {"name": "cradlepoint_routers", "display": "Cradlepoint Inventory"},
        {"name": "carrier_information_iccid1", "display": "Carrier Information (ICCID1)"},
        {"name": "carrier_information_iccid2", "display": "Carrier Information (ICCID2)"},
        {"name": "customer_installation_info", "display": "Customer Installation Information"},
    ]
    inventory_data = []

    for table in tables:
        table_name = table["name"]
        display_name = table["display"]
        # Fetch column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]  # Column names
        # Fetch rows
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        # Append data for rendering
        inventory_data.append({
            "table_name_display": display_name,  # Custom table name display
            "table_name": table_name,  # Raw table name for reference
            "columns": columns,
            "rows": rows,
            "count": count,
        })
    cursor.close()
    return render_template("full_inventory.html", inventory_data=inventory_data)






