"""
pages/profile.py
-----------------
User / workspace profile screen. Displays Account Details and Preferences
for the logged-in user in clean SaaS cards.
"""

import streamlit as st
from utils import auth
from utils.components import page_header, section_title, card, pill


def render() -> None:
    page_header(title="Profile", subtitle="Manage your account and workspace preferences.")

    user = auth.current_user() or {}
    display_name = user.get("name", "Guest")
    business_name = user.get("business_name", "—")
    email = user.get("email", "—")
    created_at = user.get("created_at", "—")
    avatar_letter = display_name.strip()[0].upper() if display_name.strip() else "?"

    col1, col2 = st.columns([1, 2])

    with col1:
        with card():
            st.markdown(
                f"""
                <div style="text-align:center;">
                    <div class="profile-avatar" style="margin:0 auto 14px auto;">{avatar_letter}</div>
                    <h4 style="margin-bottom:2px;">{display_name}</h4>
                    <p style="color:#8A96AC; margin-top:0;">{business_name}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;'>{pill('Free Plan', 'blue')} {pill('Active', 'green')}</div>",
                unsafe_allow_html=True,
            )
            st.button("Change Avatar", use_container_width=True, type="secondary")

    with col2:
        section_title("Account Details", "👤")
        with card():
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Full Name", value=display_name, disabled=True)
                st.text_input("Business Name", value=business_name, disabled=True)
            with c2:
                st.text_input("Email", value=email, disabled=True)
                st.text_input("Account Created", value=created_at, disabled=True)

        section_title("Preferences", "⚙️")
        with card():
            p1, p2 = st.columns(2)
            with p1:
                st.selectbox("Default Currency", ["USD ($)", "INR (₹)", "EUR (€)", "GBP (£)"])
                st.selectbox("Theme", ["Dark Blue (Default)", "Light", "System"])
            with p2:
                st.selectbox("Date Format", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
                st.toggle("Email me weekly summaries", value=False)
