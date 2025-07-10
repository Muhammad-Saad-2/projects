import streamlit as st
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import extra_streamlit_components as stx


load_dotenv()

BACKEND_URL=os.getenv("API_URL", "http://localhost:8000")



st.set_page_config(
    page_title="E-Commerce Auth",
    page_icon="🛍️",
    layout="centered"
)


st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-top: 20px;
    }
    .auth-form {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Cookie Manager
def get_cookie_manager():
    return stx.CookieManager()

cookie_manager = get_cookie_manager()

# API functions
def create_user(email, password, full_name, role="customer"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/register",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role
            }
        )
        if response.status_code == 200:
            st.success("✅ Account created successfully! Please login.")
            return response.json()
        else:
            st.error(f"❌ Error: {response.json().get('detail', 'Failed to create account')}")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
    return None

def login_user(email, password):
    try:
        response = requests.post(
            f"{BACKEND_URL}/token",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            result = response.json()
            save_tokens(result["access_token"], result["refresh_token"])
            return result
        else:
            st.error("❌ Invalid credentials.")
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
    return None
    

def get_user_info():
    token = cookie_manager.get("auth_token")
    if not token:
        return None
    try:
        response = requests.get(
            f"{BACKEND_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            if try_refresh_token():
                return get_user_info()
    except requests.exceptions.RequestException:
        pass
    return None

def save_tokens(auth_token, refresh_token):
    cookie_manager.set(
        "auth_token", 
        auth_token, 
        expires_at=datetime.now() + timedelta(hours=1), 
        key="auth_token_set"
    )
    cookie_manager.set(
        "refresh_token", 
        refresh_token, 
        expires_at=datetime.now() + timedelta(days=30), 
        key="refresh_token_set"
    )
    

def is_logged_in():
    token = cookie_manager.get("auth_token")
    return token is not None


def try_refresh_token():
    refresh_token = cookie_manager.get("refresh_token")
    if not refresh_token:
        return False
    try:
        response = requests.post(
            f"{BACKEND_URL}/token/refresh",
            json={"refresh_token": refresh_token}
        )
        if response.status_code == 200:
            result = response.json()
            save_tokens(result["auth_token"], result["refresh_token"])
            return True
    except:
        pass
    return False

def logout():
    # Safely delete cookies if they exist
    if "auth_token" in cookie_manager.cookies:
        cookie_manager.delete("auth_token", key="delete_auth_token")
    else:
        st.write("Auth token not found, skipping deletion.")  # Debugging line

    if "refresh_token" in cookie_manager.cookies:
        cookie_manager.delete("refresh_token", key="delete_refresh_token")
    else:
        st.write("Refresh token not found, skipping deletion.")  # Debugging line


    st.session_state.authenticated = False
    st.session_state.user_info = None

    
    st.success("👋 Logged out successfully!")

   
    st.rerun()




if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    token = cookie_manager.get("auth_token")
    if token:
        user_info = get_user_info()
        if user_info:
            st.session_state.authenticated = True
            st.session_state.user_info = user_info


with st.sidebar:
    st.title("🛍️ E-Commerce Auth")
    if not st.session_state.authenticated:
        if st.button("🔐 Login", key="sidebar_login"):
            st.session_state.page = "login"
            st.rerun()
        if st.button("📝 Sign Up", key="sidebar_signup"):
            st.session_state.page = "signup"
            st.rerun()
    else:
        st.markdown(f"### Welcome, {st.session_state.user_info['full_name']}!")
        if st.button("🚪 Logout", key="sidebar_logout"):
            logout()


if not st.session_state.authenticated:
    st.session_state.page = st.session_state.get("page", "login")
    if st.session_state.page == "login":
        st.title("🔐 Login")
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔑 Password", type="password", key="login_password")
        if st.button("🚀 Login", key="login_button"):
            if email and password:
                result = login_user(email, password)
                if result:
                    user_info = get_user_info()
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user_info = user_info
                        st.success("✅ Login successful!")
                        st.rerun()
            else:
                st.warning("⚠️ Please fill in all fields.")
    elif st.session_state.page == "signup":
        st.title("📝 Sign Up")
        full_name = st.text_input("👤 Full Name", key="signup_name")
        email = st.text_input("📧 Email", key="signup_email")
        password = st.text_input("🔑 Password", type="password", key="signup_password")
        confirm_password = st.text_input("🔄 Confirm Password", type="password", key="signup_confirm")
        if st.button("📋 Sign Up", key="signup_button"):
            if full_name and email and password and confirm_password:
                if password == confirm_password:
                    create_user(email, password, full_name)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("❌ Passwords do not match!")
            else:
                st.warning("⚠️ Please fill in all fields.")
else:
    st.title(f"🎉 Welcome, {st.session_state.user_info['full_name']}!")
    st.markdown("### 📊 Your Dashboard")
    st.write("Here is your personalized dashboard!")

