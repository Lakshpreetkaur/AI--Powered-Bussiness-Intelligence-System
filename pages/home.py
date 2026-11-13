"""
pages/home.py
-------------
Landing page for InsightIQ. Introduces the platform, provides live workspace
snapshots, and shortcuts to key workflows.
"""

import streamlit as st
from utils.components import feature_row, kpi_row, section_title
from utils import data


def render() -> None:
    has_data = data.has_dataset()
    summary = data.get_summary()

    # ---- Hero banner ----
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-eyebrow">AI-Powered Business Intelligence</div>
            <div class="hero-title">Welcome back 👋 Let's turn your sales data into decisions.</div>
            <p class="hero-text">
                InsightIQ helps you upload sales data, explore interactive dashboards,
                forecast future revenue, and get plain-English business recommendations —
                all from one clean workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📤  Upload a Dataset", use_container_width=True, type="primary"):
            if "_pages" in st.session_state and "upload" in st.session_state["_pages"]:
                st.switch_page(st.session_state["_pages"]["upload"])
    with col2:
        if st.button("📊  View Dashboard", use_container_width=True, type="secondary"):
            if "_pages" in st.session_state and "dashboard" in st.session_state["_pages"]:
                st.switch_page(st.session_state["_pages"]["dashboard"])

    # ---- Workspace Snapshot KPIs ----
    section_title("Workspace Snapshot", "🗂️")
    if has_data:
        kpi_row(
            [
                {
                    "label": "Datasets Active",
                    "value": "1 Loaded",
                    "icon": "📁",
                    "delta": f"{summary.get('rows', 0):,} records",
                    "delta_type": "positive",
                },
                {
                    "label": "Total Revenue",
                    "value": f"${summary.get('total_sales', 0):,.2f}",
                    "icon": "💰",
                    "delta": f"${summary.get('avg_order_value', 0):.2f} AOV",
                    "delta_type": "positive",
                },
                {
                    "label": "Active Forecasts",
                    "value": "Ready",
                    "icon": "🔮",
                    "delta": "Random Forest",
                    "delta_type": "positive",
                },
                {
                    "label": "AI Insights",
                    "value": "Generated",
                    "icon": "💡",
                    "delta": "Live analytics",
                    "delta_type": "positive",
                },
            ]
        )
    else:
        kpi_row(
            [
                {"label": "Datasets Uploaded", "value": "0", "icon": "📁", "delta": "Awaiting upload", "delta_type": "neutral"},
                {"label": "Active Forecasts", "value": "0", "icon": "🔮", "delta": "Not started", "delta_type": "neutral"},
                {"label": "Insights Generated", "value": "0", "icon": "💡", "delta": "Not started", "delta_type": "neutral"},
                {"label": "Reports Ready", "value": "0", "icon": "📄", "delta": "Not started", "delta_type": "neutral"},
            ]
        )

    # ---- Feature overview ----
    section_title("What you can do here", "🧭")
    feature_row(
        [
            {
                "icon": "📤",
                "title": "Upload Dataset",
                "text": "Bring in your CSV or Excel sales data and let InsightIQ prepare it for analysis.",
            },
            {
                "icon": "📊",
                "title": "Interactive Dashboard",
                "text": "Explore KPIs, trends, and charts across products, regions, and time periods.",
            },
            {
                "icon": "🔮",
                "title": "Sales Predictions",
                "text": "Forecast upcoming demand and revenue to plan ahead with confidence.",
            },
        ]
    )

    feature_row(
        [
            {
                "icon": "💡",
                "title": "Business Insights",
                "text": "Get plain-English recommendations generated from your own sales patterns.",
            },
            {
                "icon": "🧾",
                "title": "What-If Simulator",
                "text": "Simulate transaction values and profitability for new deals and scenarios.",
            },
            {
                "icon": "👤",
                "title": "Your Profile",
                "text": "Manage your workspace details and preferences in one place.",
            },
        ]
    )
