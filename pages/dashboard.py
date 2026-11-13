"""
pages/dashboard.py
-------------------
Main sales analytics dashboard.
Displays real-time KPIs, interactive filters, and Plotly charts
driven by the uploaded sales dataset.
"""

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.components import page_header, kpi_row, section_title, empty_state, card
from utils import data


def _apply_plotly_theme(fig: go.Figure) -> go.Figure:
    """Applies a clean SaaS design matching InsightIQ's aesthetic."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=25, b=15),
        font=dict(family="Inter, sans-serif", color="#1A3A6E"),
        hoverlabel=dict(bgcolor="#0D1F3C", font_size=12, font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEF1F8", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF1F8", zeroline=False)
    return fig


def render() -> None:
    has_data = data.has_dataset()
    df = data.get_dataset()

    page_header(
        title="Sales Dashboard",
        subtitle="An overview of your business performance at a glance.",
        badge="Live Dataset" if has_data else "No dataset loaded",
    )

    if not has_data or df is None or df.empty:
        with card():
            empty_state(
                title="No data to visualize yet",
                text="Upload a sales dataset or load demo data to unlock real-time revenue analytics, KPIs, and regional breakdowns.",
                icon="📈",
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("⚡ Load Demo Dataset Now", use_container_width=True, type="primary"):
                    demo_raw = data.generate_sample_sales_data(350)
                    raw_df, processed_df, summary = data.parse_and_process_file(demo_raw)
                    data.save_dataset(raw_df, processed_df, summary)
                    st.rerun()
            with c2:
                st.caption("Or go to the **Upload Dataset** page from the sidebar to upload your own CSV/Excel file.")
        return

    # ---- Filter bar ----
    with card():
        f1, f2, f3, f4 = st.columns([2, 2, 2, 1])
        with f1:
            date_options = ["All Time", "Last 30 Days", "Last 90 Days", "Year to Date"]
            selected_date_filter = st.selectbox("Date Range", date_options)
        with f2:
            available_regions = ["All Regions"] + sorted(df["Region"].dropna().unique().tolist())
            selected_region = st.selectbox("Region", available_regions)
        with f3:
            available_categories = ["All Categories"] + sorted(df["Category"].dropna().unique().tolist())
            selected_category = st.selectbox("Product Category", available_categories)
        with f4:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            reset_filters = st.button("Reset", use_container_width=True)

    # Filter dataframe
    filtered_df = df.copy()

    # Apply date filter
    if selected_date_filter != "All Time" and not reset_filters:
        max_date = filtered_df["Order_Date"].max()
        if selected_date_filter == "Last 30 Days":
            start_date = max_date - timedelta(days=30)
            filtered_df = filtered_df[filtered_df["Order_Date"] >= start_date]
        elif selected_date_filter == "Last 90 Days":
            start_date = max_date - timedelta(days=90)
            filtered_df = filtered_df[filtered_df["Order_Date"] >= start_date]
        elif selected_date_filter == "Year to Date":
            start_date = datetime(max_date.year, 1, 1)
            filtered_df = filtered_df[filtered_df["Order_Date"] >= start_date]

    # Apply categorical filters
    if selected_region != "All Regions" and not reset_filters:
        filtered_df = filtered_df[filtered_df["Region"] == selected_region]

    if selected_category != "All Categories" and not reset_filters:
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]

    if filtered_df.empty:
        st.warning("No records match the selected filters. Please adjust your criteria.")
        return

    # ---- KPI Row ----
    total_revenue = float(filtered_df["Sales"].sum())
    total_orders = len(filtered_df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
    total_profit = float(filtered_df["Profit"].sum())
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    section_title("Key Performance Indicators", "📌")
    kpi_row(
        [
            {
                "label": "Total Revenue",
                "value": f"${total_revenue:,.2f}",
                "icon": "💰",
                "delta": f"{total_orders} total orders",
                "delta_type": "positive",
            },
            {
                "label": "Total Orders",
                "value": f"{total_orders:,}",
                "icon": "🧾",
                "delta": f"Avg ${avg_order_value:.1f}/order",
                "delta_type": "neutral",
            },
            {
                "label": "Avg Order Value",
                "value": f"${avg_order_value:,.2f}",
                "icon": "🛒",
                "delta": "Per transaction",
                "delta_type": "neutral",
            },
            {
                "label": "Profit Margin",
                "value": f"{profit_margin:.1f}%",
                "icon": "📈",
                "delta": f"${total_profit:,.2f} profit",
                "delta_type": "positive" if profit_margin >= 15 else "neutral",
            },
        ]
    )

    # ---- Chart 1: Revenue Trend ----
    section_title("Revenue Trend Over Time", "📉")
    with card():
        trend_df = (
            filtered_df.set_index("Order_Date")
            .resample("ME")["Sales"]
            .sum()
            .reset_index()
        )
        trend_df.columns = ["Date", "Monthly Revenue"]

        fig_trend = px.area(
            trend_df,
            x="Date",
            y="Monthly Revenue",
            color_discrete_sequence=["#2F6FED"],
        )
        fig_trend.update_traces(
            line=dict(width=3, color="#2F6FED"),
            fillcolor="rgba(47, 111, 237, 0.12)",
        )
        _apply_plotly_theme(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": "hover", "displaylogo": False})

    # ---- Charts 2 & 3: Category & Region ----
    c1, c2 = st.columns(2)

    with c1:
        section_title("Sales by Category & Sub-Category", "🏆")
        with card():
            cat_df = (
                filtered_df.groupby(["Category", "Sub_Category"])["Sales"]
                .sum()
                .reset_index()
                .sort_values(by="Sales", ascending=False)
            )
            fig_cat = px.bar(
                cat_df,
                x="Sub_Category",
                y="Sales",
                color="Category",
                color_discrete_sequence=["#2F6FED", "#5C8DFB", "#17B26A", "#F79009"],
            )
            fig_cat.update_layout(xaxis_title="", yaxis_title="Revenue ($)", legend_title="")
            _apply_plotly_theme(fig_cat)
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": "hover", "displaylogo": False})

    with c2:
        section_title("Sales by Region", "🗺️")
        with card():
            region_df = (
                filtered_df.groupby("Region")["Sales"]
                .sum()
                .reset_index()
            )
            fig_reg = px.pie(
                region_df,
                values="Sales",
                names="Region",
                hole=0.45,
                color_discrete_sequence=["#2F6FED", "#5C8DFB", "#17B26A", "#F79009", "#8A96AC"],
            )
            _apply_plotly_theme(fig_reg)
            st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": "hover", "displaylogo": False})

    # ---- Chart 4: Top Products Table & Bar ----
    section_title("Top 10 Products by Revenue", "🏷️")
    with card():
        top_prods = (
            filtered_df.groupby(["Product_Name", "Category"])
            .agg({"Sales": "sum", "Quantity": "sum", "Profit": "sum"})
            .reset_index()
            .sort_values(by="Sales", ascending=False)
            .head(10)
        )
        fig_top = px.bar(
            top_prods.sort_values(by="Sales", ascending=True),
            x="Sales",
            y="Product_Name",
            orientation="h",
            color="Sales",
            color_continuous_scale=["#CBD4E3", "#5C8DFB", "#2F6FED"],
        )
        fig_top.update_layout(yaxis_title="", xaxis_title="Total Sales ($)", showlegend=False)
        _apply_plotly_theme(fig_top)
        st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": "hover", "displaylogo": False})
