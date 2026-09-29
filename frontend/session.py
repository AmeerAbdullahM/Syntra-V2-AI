import streamlit as st
from backend.schemas.auth import UserResponse
# pyrefly: ignore [missing-import]
from streamlit_cookies_controller import CookieController
from backend.database.connection import SessionLocal
from backend.database.repositories.user_repo import UserRepository

def get_cookie_controller():
    if "cookie_controller" not in st.session_state:
        st.session_state.cookie_controller = CookieController()
    return st.session_state.cookie_controller

def init_session():
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
        
    # Try to restore from cookie if not logged in
    if st.session_state.current_user is None:
        controller = get_cookie_controller()
        saved_email = controller.get("syntra_user_email")
        if saved_email:
            try:
                with SessionLocal() as db:
                    repo = UserRepository(db)
                    user = repo.get_by_email(saved_email)
                    if user and user.is_active:
                        st.session_state.current_user = UserResponse.model_validate(user)
            except Exception:
                pass

def get_current_user() -> UserResponse | None:
    return st.session_state.get("current_user")

def login_user(user: UserResponse):
    st.session_state.current_user = user
    controller = get_cookie_controller()
    controller.set("syntra_user_email", user.email, max_age=60*60*24*30)

def logout_user():
    st.session_state.current_user = None
    controller = get_cookie_controller()
    controller.remove("syntra_user_email")
    st.rerun()

def require_auth():
    if not get_current_user():
        st.warning("Please log in to access this page.")
        st.stop()
