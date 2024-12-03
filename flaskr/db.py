### INF601 - Advanced Programming in Python
### Justin Stewart
### Final Project
### db.py

import sqlite3
from flask import current_app, g
import click
import bcrypt
from flask import request, redirect, url_for, session, flash


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

