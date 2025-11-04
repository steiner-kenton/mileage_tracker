import streamlit as st
import supabase
from datetime import datetime

@st.cache_resource
def init_connection():
    return supabase.create_client(st.secrets["supabase"]["SUPABASE_URL"], st.secrets["supabase"]["SUPABASE_API"])

def check_session():
    """Check if there's a valid session and refresh if needed"""
    if "auth_session" in st.session_state:
        supabase_client = init_connection()
        try:
            # Get current session
            session = supabase_client.auth.get_session()
            if session:
                # Update session state with refreshed session
                st.session_state["user"] = session.user
                st.session_state["auth_session"] = session
                return True
        except Exception:
            # If session refresh fails, clear the session
            st.session_state.pop("user", None)
            st.session_state.pop("auth_session", None)
    return False

def login_or_signup():
    st.title("Login or Sign Up")

    choice = st.radio("Choose Action", ["Login", "Sign Up"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Get the initialized Supabase client
    supabase_client = init_connection()

    if choice == "Sign Up":
        if st.button("Create Account"):
            try:
                res = supabase_client.auth.sign_up({
                    "email": email,
                    "password": password
                })
                if res.user:
                    st.success("Check your email for a confirmation link.")
                    st.info("Once verified, you can log in.")
            except Exception as e:
                st.error(f"Error creating account: {str(e)}")

    elif choice == "Login":
        if st.button("Login"):
            try:
                res = supabase_client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                if res.user:
                    # Store both user and session
                    st.session_state["user"] = res.user
                    st.session_state["auth_session"] = res.session
                    st.success(f"Welcome, {res.user.email}")
                    st.rerun()  # Rerun the app to update the UI
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
