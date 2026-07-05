import os
import streamlit as st

# Credentials are read from Streamlit secrets (.streamlit/secrets.toml) or
# environment variables, never committed to source control. See
# .streamlit/secrets.toml.example for the expected format.
DEFAULT_USERS = {
    "admin": "admin123",
    "user": "user123",
}


def _load_users():
    try:
        if "users" in st.secrets:
            return dict(st.secrets["users"])
    except Exception:
        pass

    env_user = os.environ.get("APP_USERNAME")
    env_pass = os.environ.get("APP_PASSWORD")
    if env_user and env_pass:
        return {env_user: env_pass}

    # Fallback so the demo still runs out of the box. Replace these before
    # deploying anywhere public.
    return DEFAULT_USERS


def authenticate():
    st.title("Login - Analisis Produktivitas Padi")

    users = _load_users()

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

        if submit_button:
            if username in users and users[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah!")
