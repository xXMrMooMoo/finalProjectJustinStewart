### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### db.py

import click
import sqlite3
from flask import current_app, g
import bcrypt
import sys


def get_db_standalone():
    """Standalone connection to the SQLite database."""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn


def add_admin_user_standalone(username, password):
    """Add a new admin user when running as a standalone script."""
    conn = get_db_standalone()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return "Admin user created successfully."
    except sqlite3.IntegrityError:
        return "Username already exists."
    finally:
        conn.close()

#   added this to handle handling regarding adding admin users from the cli
if __name__ == "__main__":
    # Check for CLI arguments
    if len(sys.argv) != 3:
        print("Usage: python db.py <username> <password>")
    else:
        # Extract username and password from arguments
        username, password = sys.argv[1], sys.argv[2]

        # Add user
        print(add_admin_user_standalone(username, password))


def get_db():
    """Establish a connection to the SQLite database."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db



def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
def init_db():
    """CLI command to initialize the database."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    click.echo("Initialized the database.")



def add_admin_user(username, password):
    """Add a new admin user with a hashed password."""
    db = get_db()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        db.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return "Username already exists."
    return "Admin user created successfully."

def verify_admin_user(username, password):
    """Verify an admin user's credentials."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM admin_users WHERE username = ?", (username,)
    ).fetchone()
    if user is None:
        return False
    return bcrypt.checkpw(password.encode('utf-8'), user["password_hash"])

def delete_admin_user(username):
    """Delete an admin user by username."""
    db = get_db()
    db.execute("DELETE FROM admin_users WHERE username = ?", (username,))
    db.commit()
    return f"Admin user {username} deleted successfully."

def delete_admin_user(username):
    """Delete an admin user by username."""
    db = get_db()
    user = db.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    if user:
        db.execute("DELETE FROM admin_users WHERE username = ?", (username,))
        db.commit()
        return f"User {username} deleted successfully."
    else:
        return f"User {username} does not exist."


def reinitialize_database():
    """Reinitialize the database, dropping and recreating non-admin tables."""
    db = get_db()
    with current_app.open_resource("reinitialize_schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    return "Database reinitialized (admin_users table preserved)."



def list_admin_users():
    """List all admin usernames."""
    db = get_db()
    users = db.execute("SELECT username FROM admin_users").fetchall()
    return [user["username"] for user in users]

def get_admin_user(username):
    """Retrieve an admin user by username."""
    db = get_db()
    user = db.execute("SELECT * FROM admin_users WHERE username = ?", (username,)).fetchone()
    return user


