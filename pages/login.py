"""
pages/login.py
---------------
Login screen. On success, saves the user in
st.session_state via utils.auth and redirects to the Dashboard.
"""

import streamlit as st

from utils import auth
from utils.components import page_header, card


def render(switch_to_signup=None, on_success=None) -> None:
    left, mid, right = st.columns([1, 1.3, 1])

    with mid:
        page_header(title="Welcome Back", subtitle="Log in to your InsightIQ workspace.")

        with card():
            with st.form("login_form", border=False):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("🔐  Log In", use_container_width=True)

            if submitted:
                success, message = auth.login(email, password)
                if success:
                    st.success(message)
                    if on_success:
                        on_success()
                    else:
                        st.rerun()
                else:
                    st.error(message)

        st.markdown(
            "<p style='text-align:center; color:#8A96AC; margin-top: 10px;'>Don't have an account?</p>",
            unsafe_allow_html=True,
        )
        if switch_to_signup:
            st.button("Create an Account", use_container_width=True, type="secondary", on_click=switch_to_signup)
