
import re
import bcrypt

from database import create_user, get_user_by_email


def validate_signup(full_name, email, password, confirm_password):
    full_name = full_name.strip()
    email = email.strip().lower()

    if len(full_name) < 2:
        return False, "Please enter your full name."

    if len(full_name) > 100:
        return False, "Your name must be 100 characters or fewer."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must be 72 bytes or fewer."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    return True, "Signup details are valid."


def signup(full_name, email, password, confirm_password):
    valid, message = validate_signup(
        full_name,
        email,
        password,
        confirm_password,
    )

    if not valid:
        return False, message

    email = email.strip().lower()

    if get_user_by_email(email):
        return False, "An account with this email already exists."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

    user = create_user(
        full_name=full_name.strip(),
        email=email,
        password_hash=password_hash,
    )

    if not user:
        return False, "An account with this email already exists."

    return True, "Account created successfully!"


def login(email, password):
    email = email.strip().lower()

    user = get_user_by_email(email)

    if not user:
        return False, "Invalid email or password.", None

    try:
        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )
    except (ValueError, TypeError):
        password_matches = False

    if not password_matches:
        return False, "Invalid email or password.", None

    safe_user = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
    }

    return True, "Login successful!", safe_user
