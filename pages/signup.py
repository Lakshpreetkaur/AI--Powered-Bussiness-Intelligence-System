"""
pages/signup.py
----------------
Account creation screen. Validates input and
stores the new user (hashed password) via utils.auth / utils.database.
"""

import streamlit as st

from utils import auth
from utils.components import page_header, card


def render(switch_to_login=None) -> None:
    left, mid, right = st.columns([1, 1.3, 1])

    with mid:
        page_header(title="Create Your Account", subtitle="Set up your InsightIQ workspace in seconds.")

        with card():
            with st.form("signup_form", border=False):
                name = st.text_input("Full Name", placeholder="Jane Doe")
                email = st.text_input("Email", placeholder="you@example.com")
                business_name = st.text_input("Business Name", placeholder="Acme Retail Co.")
                password = st.text_input("Password", type="password", placeholder="At least 6 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submitted = st.form_submit_button("📝  Create Account", use_container_width=True)

            if submitted:
                success, message = auth.signup(
                    name=name,
                    email=email,
                    password=password,
                    confirm_password=confirm_password,
                    business_name=business_name,
                )
                if success:
                    st.success(message)
                    if switch_to_login:
                        st.button("Go to Login", use_container_width=True, on_click=switch_to_login)
                else:
                    st.error(message)

        st.markdown(
            "<p style='text-align:center; color:#8A96AC; margin-top: 10px;'>Already have an account?</p>",
            unsafe_allow_html=True,
        )
        if switch_to_login:
            st.button("Log In Instead", use_container_width=True, type="secondary", on_click=switch_to_login)
