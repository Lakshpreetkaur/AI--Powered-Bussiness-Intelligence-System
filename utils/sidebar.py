"""
utils/sidebar.py
-----------------
Sidebar branding header and footer, rendered on every page above/below
the navigation links that st.navigation() generates automatically.
"""

import streamlit as st


def render_sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">📊</div>
                <div>
                    <div class="sidebar-brand-text">InsightIQ</div>
                    <div class="sidebar-brand-sub">Sales Intelligence</div>
                </div>
            </div>
            <hr class="sidebar-divider">
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_footer(user_name: str = "Guest User", plan: str = "Free Plan", on_logout=None) -> None:
    with st.sidebar:
        st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="sidebar-footer">
                <b style="color:#E4E9F5 !important;">{user_name}</b><br>
                {plan}<br>
                <span style="opacity:0.6;">InsightIQ v0.1.0 &middot; UI Preview</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Logout control — only rendered when a handler is supplied
        # (i.e. when a user is actually logged in).
        if on_logout:
            st.button("🚪  Logout", use_container_width=True, type="secondary", on_click=on_logout)
