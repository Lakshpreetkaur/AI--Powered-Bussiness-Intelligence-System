"""
utils/auth.py
--------------
Authentication logic for InsightIQ: password hashing, input
validation, signup/login flows, and Streamlit session-state helpers.
This is the only layer pages should talk to — pages never touch
utils/database.py directly.
"""

import re
import hashlib
import hmac
import os

import streamlit as st

from utils import database as db

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SESSION_KEY = "auth_user"


# ---------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256, salted, no extra dependencies)
# ---------------------------------------------------------------------
def _hash_password(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, digest_hex = stored_hash.split("$")
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(candidate.hex(), digest_hex)


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------
def is_valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email.strip()))


# ---------------------------------------------------------------------
# Signup / Login
# ---------------------------------------------------------------------
def signup(name: str, email: str, password: str, confirm_password: str, business_name: str):
    """
    Attempt to create a new user account.
    Returns (success: bool, message: str).
    """
    name = (name or "").strip()
    email = (email or "").strip()
    business_name = (business_name or "").strip()

    if not name or not email or not password or not business_name:
        return False, "Please fill in all fields."

    if not is_valid_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if password != confirm_password:
        return False, "Passwords do not match."

    db.init_db()
    if db.email_exists(email):
        return False, "An account with this email already exists."

    password_hash = _hash_password(password)
    db.create_user(name=name, email=email, password_hash=password_hash, business_name=business_name)
    return True, "Account created successfully! You can now log in."


def login(email: str, password: str):
    """
    Attempt to authenticate a user.
    Returns (success: bool, message: str).
    """
    email = (email or "").strip()

    if not email or not password:
        return False, "Please enter both email and password."

    db.init_db()
    user = db.get_user_by_email(email)
    if not user or not _verify_password(password, user["password_hash"]):
        return False, "Invalid email or password."

    _login_session(user)
    return True, "Login successful!"


# ---------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------
def _login_session(user: dict) -> None:
    st.session_state[SESSION_KEY] = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "business_name": user["business_name"],
        "created_at": user["created_at"],
    }


def is_authenticated() -> bool:
    return SESSION_KEY in st.session_state


def current_user():
    """Return the logged-in user's dict, or None if not authenticated."""
    return st.session_state.get(SESSION_KEY)


def logout() -> None:
    st.session_state.pop(SESSION_KEY, None)
