import streamlit as st
from backend.schemas.auth import UserResponse

def init_session():
    if "current_user" not in st.session_state:
        st.session_state.current_user = None

def get_current_user() -> UserResponse | None:
    return st.session_state.get("current_user")

def login_user(user: UserResponse):
    st.session_state.current_user = user

def logout_user():
    st.session_state.current_user = None
    st.rerun()

def require_auth():
    if not get_current_user():
        st.warning("Please log in to access this page.")
        st.stop()
