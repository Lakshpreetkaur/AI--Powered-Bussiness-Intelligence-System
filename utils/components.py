"""
utils/components.py
--------------------
Reusable, styled UI building blocks used across every InsightIQ page.
Keeping these as small functions means every page stays short and
consistent instead of re-writing markup everywhere.
"""

from contextlib import contextmanager

import streamlit as st


@contextmanager
def card():
    """Wrap content in a styled SaaS card container."""
    with st.container(border=True):
        yield


def card_start() -> None:
    """Deprecated no-op to prevent empty unclosed white boxes."""
    pass


def card_end() -> None:
    """Deprecated no-op."""
    pass


def page_header(title: str, subtitle: str = "", badge: str = "") -> None:
    """Top-of-page title + subtitle + optional status badge."""
    badge_html = f'<div class="page-badge">{badge}</div>' if badge else ""
    st.markdown(
        f"""
        <div class="page-header">
            <div>
                <p class="page-title">{title}</p>
                <p class="page-subtitle">{subtitle}</p>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str, icon: str = "") -> None:
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, icon: str = "📈", delta: str = "", delta_type: str = "neutral") -> str:
    """
    Return HTML for a single KPI card.
    delta_type: 'positive' | 'negative' | 'neutral'
    """
    delta_html = ""
    if delta:
        arrow = "▲" if delta_type == "positive" else "▼" if delta_type == "negative" else "•"
        delta_html = f'<div class="kpi-delta {delta_type}">{arrow} {delta}</div>'

    return f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def kpi_row(cards: list[dict]) -> None:
    """
    Render a responsive row of KPI cards.
    cards: list of dicts with keys: label, value, icon, delta, delta_type
    """
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        with col:
            st.markdown(
                kpi_card(
                    label=card.get("label", ""),
                    value=card.get("value", ""),
                    icon=card.get("icon", "📈"),
                    delta=card.get("delta", ""),
                    delta_type=card.get("delta_type", "neutral"),
                ),
                unsafe_allow_html=True,
            )


def feature_tile(title: str, text: str, icon: str = "✨") -> str:
    return f"""
    <div class="feature-tile">
        <div class="feature-tile-icon">{icon}</div>
        <div class="feature-tile-title">{title}</div>
        <div class="feature-tile-text">{text}</div>
    </div>
    """


def feature_row(tiles: list[dict]) -> None:
    cols = st.columns(len(tiles))
    for col, tile in zip(cols, tiles):
        with col:
            st.markdown(
                feature_tile(tile.get("title", ""), tile.get("text", ""), tile.get("icon", "✨")),
                unsafe_allow_html=True,
            )


def empty_state(title: str, text: str, icon: str = "📭") -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="empty-state-icon">{icon}</div>
            <div class="empty-state-title">{title}</div>
            <div class="empty-state-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def pill(text: str, color: str = "blue") -> str:
    return f'<span class="pill pill-{color}">{text}</span>'
