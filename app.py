"""
app.py
------
InsightIQ — AI Sales Business Intelligence Platform
Main entrypoint: wires up page config, global styling, and navigation.

Authentication gate:
- If no user is logged in, only Login / Sign Up pages are reachable.
- Once authenticated, the original app navigation (Overview / Workflow /
  Account) is restored exactly as before, and the user lands on the
  Dashboard (required by the auth spec: "redirect to Dashboard").

Run with:  streamlit run app.py
"""

import streamlit as st

# ---- Page config must be the first Streamlit call ----
from utils.styling import set_page_config, load_css
set_page_config()

# ---- Global theme ----
load_css()

from utils.sidebar import render_sidebar_brand, render_sidebar_footer
from utils import auth, database
from pages import home, dashboard, upload, predictions, insights, profile, login, signup

# ---- Ensure the users table exists ----
database.init_db()

# ---- Sidebar brand header ----
render_sidebar_brand()

if auth.is_authenticated():
    user = auth.current_user()

    # ---- App pages ----
    home_page = st.Page(home.render, title="Home", icon="🏠", url_path="home")
    dashboard_page = st.Page(dashboard.render, title="Dashboard", icon="📊", default=True, url_path="dashboard")
    upload_page = st.Page(upload.render, title="Upload Dataset", icon="📤", url_path="upload")
    predictions_page = st.Page(predictions.render, title="Predictions", icon="🔮", url_path="predictions")
    insights_page = st.Page(insights.render, title="Business Insights", icon="💡", url_path="insights")
    profile_page = st.Page(profile.render, title="Profile", icon="👤", url_path="profile")

    # Store page handles in session state for cross-page button navigation
    st.session_state["_pages"] = {
        "home": home_page,
        "dashboard": dashboard_page,
        "upload": upload_page,
        "predictions": predictions_page,
        "insights": insights_page,
        "profile": profile_page,
    }

    # ---- Grouping/order ----
    nav = st.navigation(
        {
            "Overview": [home_page, dashboard_page],
            "Workflow": [upload_page, predictions_page, insights_page],
            "Account": [profile_page],
        }
    )

    # ---- Sidebar footer shows real logged-in user + Logout ----
    render_sidebar_footer(user_name=user["name"], plan="Free Plan", on_logout=auth.logout)

    nav.run()

else:
    # ---- Unauthenticated: only Login / Sign Up are reachable ----
    login_page = st.Page(
        lambda: login.render(switch_to_signup=lambda: st.switch_page(signup_page)),
        title="Login",
        icon="🔐",
        default=True,
        url_path="login",
    )
    signup_page = st.Page(
        lambda: signup.render(switch_to_login=lambda: st.switch_page(login_page)),
        title="Sign Up",
        icon="📝",
        url_path="signup",
    )

    nav = st.navigation([login_page, signup_page])

    render_sidebar_footer(user_name="Guest", plan="Not logged in")

    nav.run()
