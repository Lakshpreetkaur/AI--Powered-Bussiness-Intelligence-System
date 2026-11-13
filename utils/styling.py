"""
utils/styling.py
-----------------
Handles global page configuration and injection of the custom
InsightIQ CSS theme. Keeping this separate from app.py keeps the
entrypoint clean and makes the theme reusable across every page.
"""

from pathlib import Path
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CSS_FILE = ASSETS_DIR / "style.css"


def load_css() -> None:
    """Inject the custom stylesheet into the current Streamlit page."""
    if CSS_FILE.exists():
        css = CSS_FILE.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def set_page_config(page_title: str = "InsightIQ", page_icon: str = "📊") -> None:
    """Apply consistent page config across every page in the app."""
    st.set_page_config(
        page_title=f"{page_title} | InsightIQ",
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
