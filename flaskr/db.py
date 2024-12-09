### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### db.py

import click  # Used for creating CLI commands
from flask import current_app, g  # Flask context and global object for database connections
import argparse  # Handles CLI argument parsing
import sqlite3  # SQLite database interaction
import bcrypt  # Password hashing and verification


# Function to establish a standalone connection to the SQLite database
def get_db_standalone():
    """Standalone connection to the SQLite database."""
    conn = sqlite3.connect('data.db')  # Connects to the database file
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    return conn


# Function to add an admin user when the script is run standalone (not via Flask)
def add_admin_user_standalone(username, password):
    conn = get_db_standalone()
    # Hash the provided password for secure storage
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        # Insert the username and hashed password into the database
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()  # Commit the transaction
        print("Admin user created successfully.")
    except sqlite3.OperationalError as e:
        # Handles the case where the `admin_users` table does not exist
        if "no such table" in str(e):
            print("Error: The 'admin_users' table does not exist. Initialize the database first.")
        else:
            raise  # Re-raise other unexpected errors
    except sqlite3.IntegrityError:
        # Handles the case where the username already exists in the database
        print("Username already exists.")
    finally:
        conn.close()  # Ensure the connection is closed


# CLI functionality for standalone execution of the script
if __name__ == "__main__":
    # Create a parser to handle CLI arguments
    parser = argparse.ArgumentParser(description="Manage the SQLite database.")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Add the `AddAdminUser` subcommand
    add_user_parser = subparsers.add_parser("AddAdminUser", help="Add an admin user.")
    add_user_parser.add_argument("username", help="The username for the admin user.")
    add_user_parser.add_argument("password", help="The password for the admin user.")

    args = parser.parse_args()

    # Execute the addadminuser command
    if args.command == "AddAdminUser":
        add_admin_user_standalone(args.username, args.password)


# Function to get a database connection within a Flask app context
def get_db():
    if 'db' not in g:  # Check if the database connection is already stored in Flask's global `g`
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],  # Use Flask's configured database path
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
    return g.db


# Function to close the database connection at the end of a request
def close_db(e=None):
    db = g.pop('db', None)  # Remove the database connection from Flask's global `g`
    if db is not None:
        db.close()  # Close the connection if it exists


# CLI command to initialize the database
@click.command('init-db')
def init_db():
    db = get_db()
    # Load and execute the SQL schema
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    click.echo("Initialized the database.")


# Function to add an admin user through Flask
def add_admin_user(username, password):
    db = get_db()
    # Hash the password securely
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        # Insert the user data into the database
        db.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return "Username already exists."  # Return an error if the username is not unique
    return "Admin user created successfully."


# Function to verify an admin user's login credentials
def verify_admin_user(username, password):
    """Verify an admin user's credentials."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM admin_users WHERE username = ?", (username,)
    ).fetchone()  # Fetch the user record
    if user is None:
        return False  # Return False if the user does not exist
    # Verify the provided password against the stored hash
    return bcrypt.checkpw(password.encode('utf-8'), user["password_hash"])


# Function to delete an admin user by username
def delete_admin_user(username):
    db = get_db()
    # Check if the user exists
    user = db.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    if user:
        # Delete the user if they exist
        db.execute("DELETE FROM admin_users WHERE username = ?", (username,))
        db.commit()
        return f"User {username} deleted successfully."
    else:
        return f"User {username} does not exist."


# Function to reinitialize the database while preserving the `admin_users` table
def reinitialize_database():
    db = get_db()
    with current_app.open_resource("reinitialize_schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    return "Database reinitialized (admin_users table preserved)."


# Function to list all admin usernames
def list_admin_users():
    db = get_db()
    users = db.execute("SELECT username FROM admin_users").fetchall()  # Fetch all usernames
    return [user["username"] for user in users]  # Return the usernames as a list


# Function to get an admin user by username
def get_admin_user(username):
    db = get_db()
    user = db.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    return user
