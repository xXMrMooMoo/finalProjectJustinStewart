### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### app.py

from flask import Flask, render_template
import db  # Import the database module
from flask import request, redirect, url_for, session, flash
from functions import *  # Custom functions for additional functionality

# Initialize the Flask app
app = Flask(__name__)
start_logging()
app.secret_key = 'your_secret_key'  # Secret key for session management

# Configuration for the SQLite database
app.config['DATABASE'] = 'data.db'

# Register teardown and database commands
app.teardown_appcontext(db.close_db)  # Ensure database connection is closed after each request
app.cli.add_command(db.init_db)  # Register a command to initialize the database

# Define the route for the home page
@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    """
    Handles admin login functionality.
    On POST: Checks the provided credentials and logs the user in if valid.
    On GET: Displays the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user exists
        user_exists = db.get_admin_user(username)
        if not user_exists:
            flash(f"Incorrect username: {username}", "danger")
        elif not db.verify_admin_user(username, password):
            flash(f"Incorrect password for username: {username}", "danger")
        else:
            # Successful login
            session["admin_logged_in"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

@app.route("/admin-logout")
def admin_logout():
    """
    Logs out the currently logged-in admin.
    Clears session data and redirects to the home page.
    """
    username = session.get("admin_username", "Unknown User")
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash(f"User: {username} logged out.", "info")
    return redirect(url_for("home"))

@app.route("/admin-dashboard", methods=["GET", "POST"])
def admin_dashboard():
    """
    Displays the admin dashboard, allowing the admin to:
    - Create new admin users
    - Delete existing admin users
    - Reinitialize the database
    """
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        if "create_user" in request.form:
            # Handle user creation
            username = request.form.get("username")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if password != confirm_password:
                flash("Passwords do not match. Please try again.", "danger")
            else:
                message = db.add_admin_user(username, password)
                if "already exists" in message:
                    flash(message, "danger")
                else:
                    flash(f"Admin user '{username}' created successfully.", "success")

        elif "delete_user" in request.form:
            # Handle user deletion
            username = request.form.get("username")
            message = db.delete_admin_user(username)
            flash(message, "info")

        elif "reinit_db" in request.form:
            # Handle database reinitialization
            message = db.reinitialize_database()
            flash(message, "warning")

    admin_users = db.list_admin_users()
    return render_template("admin_dashboard.html", admin_users=admin_users)

@app.context_processor
def inject_user_status():
    """
    Injects the admin's login status and username into all templates.
    Useful for showing dynamic content based on login state.
    """
    is_logged_in = session.get("admin_logged_in", False)
    username = session.get("admin_username") if is_logged_in else None
    return {"is_logged_in": is_logged_in, "username": username}

@app.route("/full-inventory")
def full_inventory():
    """
    Displays the full inventory of routers and related information.
    Fetches data from multiple tables and renders them for display.
    """
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    # Define tables and their display names
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

        # Fetch table data
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [col[1] for col in cursor.fetchall()]  # Column names
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]

        inventory_data.append({
            "table_name_display": display_name,
            "table_name": table_name,
            "columns": columns,
            "rows": rows,
            "count": count,
        })

    cursor.close()
    return render_template("full_inventory.html", inventory_data=inventory_data)

@app.route("/router-status-lookup", methods=["GET", "POST"])
def router_status_lookup():
    """
    Allows the admin to look up the status of a router by its ID.
    Fetches data from the Cradlepoint API if the router exists.
    """
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    # Fetch all routers for display
    cursor.execute("PRAGMA table_info(cradlepoint_routers);")
    columns = [col[1] for col in cursor.fetchall()]
    cursor.execute("SELECT * FROM cradlepoint_routers;")
    rows = cursor.fetchall()

    status_message = None

    if request.method == "POST":
        router_id = request.form.get("router_id")
        cursor.execute("SELECT router_id FROM cradlepoint_routers WHERE router_id = ?", (router_id,))
        result = cursor.fetchone()

        try:
            if result is not None:
                # Fetch router status from the Cradlepoint API
                cradlepoint_headers = return_headers_configparser("root_rw.ini")
                url = f'https://www.cradlepointecm.com/api/v2/routers/{router_id}/'
                response = get_with_retry(url, cradlepoint_headers)

                if response is None:
                    status_message = "Router API call error. Please check the router with the administrator."
                else:
                    router_status = response.json()['state']
                    router_status_change = response.json()['updated_at']
                    status_message = f'Router {router_id} {router_status} since {router_status_change}'
            else:
                status_message = f"Router ID {router_id} not found in the inventory."
        except Exception:
            status_message = f'Router ID {router_id} not found via API call, or missing API keys.'

    cursor.close()
    return render_template("router_status_lookup.html", columns=columns, rows=rows, status_message=status_message)

@app.route("/router-detail-finder", methods=["GET", "POST"])
def router_detail_finder():
    """
    Allows the admin to search for router details using a MAC address.
    Provides case-insensitive matching for MAC addresses.
    """
    db_connection = db.get_db()
    cursor = db_connection.cursor()

    # Fetch all MAC addresses
    cursor.execute("SELECT cradlepoint_mac_address FROM cradlepoint_routers;")
    macs = [row[0] for row in cursor.fetchall()]

    details = None
    error_message = None

    if request.method == "POST":
        mac_address = request.form.get("mac_address").strip()

        # Validate MAC address format
        import re
        if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac_address):
            error_message = "Invalid MAC address format. Please enter a valid MAC address."
        else:
            # Check for MAC address existence (case-insensitive)
            cursor.execute("SELECT 1 FROM cradlepoint_routers WHERE LOWER(cradlepoint_mac_address) = LOWER(?)", (mac_address,))
            if cursor.fetchone() is None:
                error_message = f"MAC address {mac_address} not found in the database."
            else:
                query = """
                SELECT
                    r.router_id,
                    r.cradlepoint_mac_address,
                    r.model,
                    r.iccid1,
                    r.iccid2,
                    c.customer_account_number,
                    c.customer_address,
                    i1.provisioning_status AS iccid1_provisioning_status,
                    i2.provisioning_status AS iccid2_provisioning_status
                FROM
                    cradlepoint_routers r
                LEFT JOIN
                    customer_installation_info c ON LOWER(r.cradlepoint_mac_address) = LOWER(c.cradlepoint_mac_address)
                LEFT JOIN
                    carrier_information_iccid1 i1 ON r.iccid1 = i1.iccid
                LEFT JOIN
                    carrier_information_iccid2 i2 ON r.iccid2 = i2.iccid
                WHERE
                    LOWER(r.cradlepoint_mac_address) = LOWER(?);
                """
                cursor.execute(query, (mac_address,))
                details = cursor.fetchone()

    cursor.close()
    return render_template("router_detail_finder.html", macs=macs, details=details, error_message=error_message)

@app.route("/add-a-router", methods=["GET", "POST"])
def add_a_router():
    """
    Allows the admin to add a new router to the database.
    Ensures unique MAC addresses (case-insensitive) and normalizes them to uppercase.
    """
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    error_message = None
    form_data = {}

    if request.method == "POST":
        form_data = {
            "router_id": request.form.get("router_id"),
            "mac_address": request.form.get("mac_address").strip().upper(),
            "model": request.form.get("model"),
            "iccid1": request.form.get("iccid1"),
            "iccid2": request.form.get("iccid2"),
            "customer_account_number": request.form.get("customer_account_number"),
            "customer_address": request.form.get("customer_address"),
            "iccid1_status": request.form.get("iccid1_status"),
            "iccid2_status": request.form.get("iccid2_status"),
        }

        try:
            db_connection = db.get_db()
            cursor = db_connection.cursor()

            cursor.execute(
                "SELECT 1 FROM cradlepoint_routers WHERE LOWER(cradlepoint_mac_address) = LOWER(?)",
                (form_data["mac_address"],)
            )
            if cursor.fetchone():
                raise ValueError("MAC Address is not unique. Please use a different MAC Address.")

            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute(
                """
                INSERT INTO cradlepoint_routers (router_id, cradlepoint_mac_address, model, iccid1, iccid2)
                VALUES (?, upper(?), ?, ?, ?);
                """,
                (form_data["router_id"], form_data["mac_address"], form_data["model"], form_data["iccid1"], form_data["iccid2"])
            )

            cursor.execute(
                """
                INSERT INTO customer_installation_info (customer_account_number, cradlepoint_mac_address, customer_address)
                VALUES (?, ?, ?);
                """,
                (form_data["customer_account_number"], form_data["mac_address"], form_data["customer_address"])
            )

            cursor.execute(
                """
                INSERT INTO carrier_information_iccid1 (iccid, provisioning_status)
                VALUES (?, ?);
                """,
                (form_data["iccid1"], form_data["iccid1_status"])
            )

            cursor.execute(
                """
                INSERT INTO carrier_information_iccid2 (iccid, provisioning_status)
                VALUES (?, ?);
                """,
                (form_data["iccid2"], form_data["iccid2_status"])
            )

            db_connection.commit()
            flash(f"Router with MAC: {form_data['mac_address'].upper()}, Router ID: {form_data['router_id']} added successfully!", "success")
            return redirect(url_for("add_a_router"))
        except ValueError as ve:
            error_message = str(ve)
            flash(error_message, "danger")
        except Exception as e:
            db_connection.rollback()
            error_message = str(e)
            if "UNIQUE constraint failed" in str(e):
                if "router_id" in str(e):
                    error_message = "Router ID is not unique. Please use a different ID."
                elif "cradlepoint_mac_address" in str(e):
                    error_message = "MAC Address is not unique. Please use a different MAC Address."
                elif "iccid1" in str(e):
                    error_message = "ICCID1 is not unique. Please use a different ICCID1."
                elif "iccid2" in str(e):
                    error_message = "ICCID2 is not unique. Please use a different ICCID2."
            flash(error_message, "danger")
        finally:
            cursor.close()

    return render_template("add_a_router.html", error_message=error_message, form_data=form_data)
