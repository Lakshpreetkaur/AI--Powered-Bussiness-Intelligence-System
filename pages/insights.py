"""
pages/insights.py
------------------
Plain-English, AI-generated business insights and recommendations.
Dynamically computed from the active sales dataset to surface top opportunities,
inventory alerts, seasonal trends, and natural-language Q&A.
"""

import pandas as pd
import streamlit as st

from utils.components import page_header, section_title, empty_state, card, pill
from utils import data


def render() -> None:
    has_data = data.has_dataset()
    df = data.get_dataset()

    page_header(
        title="Business Insights",
        subtitle="Plain-English recommendations generated from your sales data.",
        badge="Insights Ready" if has_data else "Awaiting data",
    )

    if not has_data or df is None or df.empty:
        with card():
            empty_state(
                title="No insights available yet",
                text="Upload a sales dataset or load demo data to unlock automated business intelligence and actionable recommendations.",
                icon="💡",
            )
            if st.button("⚡ Load Demo Dataset Now", type="primary"):
                demo_raw = data.generate_sample_sales_data(350)
                raw_df, processed_df, summary = data.parse_and_process_file(demo_raw)
                data.save_dataset(raw_df, processed_df, summary)
                st.rerun()
        return

    # Dynamic metrics computation
    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())

    # Category insights
    cat_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    top_cat = cat_sales.index[0]
    top_cat_share = (cat_sales.iloc[0] / total_sales) * 100 if total_sales > 0 else 0

    # Region insights
    region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    top_region = region_sales.index[0]
    top_region_sales = region_sales.iloc[0]

    # Discount impact
    discounted = df[df["Discount"] > 0]
    full_price = df[df["Discount"] == 0]
    disc_margin = (discounted["Profit"].sum() / discounted["Sales"].sum() * 100) if not discounted.empty and discounted["Sales"].sum() > 0 else 0
    full_margin = (full_price["Profit"].sum() / full_price["Sales"].sum() * 100) if not full_price.empty and full_price["Sales"].sum() > 0 else 0

    # Seasonal & timing
    weekend_sales = df[df["Is_Weekend"] == 1]["Sales"].sum()
    weekend_pct = (weekend_sales / total_sales * 100) if total_sales > 0 else 0

    # Monthly peak
    monthly = df.groupby("Order_Month")["Sales"].sum()
    peak_month_num = monthly.idxmax()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    peak_month = month_names[peak_month_num - 1]

    tabs = st.tabs(["💡 Key Insights", "📦 Inventory & Demand", "📅 Seasonal Trends", "❓ Ask a Question"])

    # ---- Tab 1: Key Insights ----
    with tabs[0]:
        col1, col2 = st.columns(2)

        with col1:
            with card():
                st.markdown(f"#### 🚀 Primary Growth Driver: **{top_cat}**")
                st.markdown(
                    f"**{top_cat}** generates **${cat_sales.iloc[0]:,.2f}**, representing **{top_cat_share:.1f}%** of your total sales volume. "
                    "Consider increasing advertising spend and cross-selling bundles around this high-performing line."
                )
                st.markdown(pill(f"Top Performer: {top_cat}", "blue"), unsafe_allow_html=True)

            with card():
                st.markdown(f"#### 🌍 Geographic Leader: **{top_region}**")
                st.markdown(
                    f"The **{top_region}** market leads with **${top_region_sales:,.2f}** in orders. "
                    f"It is currently outperforming {region_sales.index[-1]} by **{(top_region_sales / max(region_sales.iloc[-1], 1)):.1f}x**."
                )
                st.markdown(pill(f"Strongest Region: {top_region}", "green"), unsafe_allow_html=True)

        with col2:
            with card():
                st.markdown("#### 🏷️ Pricing & Discount Sensitivity")
                st.markdown(
                    f"Full-price orders average a healthy **{full_margin:.1f}%** profit margin, whereas discounted orders yield **{disc_margin:.1f}%**. "
                    + ("⚠️ Heavy discounts are significantly eroding net margins. Recommend capping promotional discounts at 15%." if (full_margin - disc_margin) > 10 else "Discounts are currently healthy and sustainable.")
                )
                st.markdown(pill(f"Margin Spread: {abs(full_margin - disc_margin):.1f}%", "orange" if (full_margin - disc_margin) > 10 else "green"), unsafe_allow_html=True)

            with card():
                st.markdown("#### 📦 Delivery & Shipping Efficiency")
                avg_ship = df["Shipping_Days"].mean()
                st.markdown(
                    f"Average fulfillment duration is **{avg_ship:.1f} days**. "
                    + ("Fulfillment turnaround is rapid and meets top industry standards." if avg_ship <= 4 else "Shipping duration exceeds 4 days. Consider local hub distribution to improve customer satisfaction.")
                )
                st.markdown(pill(f"Avg Shipping: {avg_ship:.1f} Days", "blue"), unsafe_allow_html=True)

    # ---- Tab 2: Inventory ----
    with tabs[1]:
        with card():
            st.markdown("#### ⚡ Fast-Moving Items (Restock Priority)")
            fast_movers = (
                df.groupby(["Product_Name", "Sub_Category"])
                .agg({"Quantity": "sum", "Sales": "sum"})
                .reset_index()
                .sort_values(by="Quantity", ascending=False)
                .head(5)
            )
            fast_movers.columns = ["Product", "Sub-Category", "Units Sold", "Total Revenue ($)"]
            st.dataframe(fast_movers, use_container_width=True)
            st.caption("These items have the highest sales velocity. Maintain minimum 30-day buffer inventory.")

        with card():
            st.markdown("#### ⚠️ Low Velocity & Capital Tied Up")
            slow_movers = (
                df.groupby(["Product_Name", "Sub_Category"])
                .agg({"Quantity": "sum", "Sales": "sum", "Discount": "mean"})
                .reset_index()
                .sort_values(by="Quantity", ascending=True)
                .head(5)
            )
            slow_movers.columns = ["Product", "Sub-Category", "Units Sold", "Total Revenue ($)", "Avg Discount"]
            st.dataframe(slow_movers, use_container_width=True)
            st.caption("Consider promotional clearance campaigns or bundling these items with top performers.")

    # ---- Tab 3: Seasonal Trends ----
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            with card():
                st.markdown(f"#### 📅 Peak Revenue Month: **{peak_month}**")
                st.markdown(
                    f"Sales reached their highest point during **{peak_month}** with **${monthly.max():,.2f}** in transactions. "
                    "Plan marketing budgets and inventory procurement 45 days in advance of this month."
                )
        with c2:
            with card():
                st.markdown("#### 🗓️ Weekend vs. Weekday Dynamics")
                st.markdown(
                    f"Weekend purchases account for **{weekend_pct:.1f}%** of total sales (${weekend_sales:,.2f}), while weekdays drive **{100 - weekend_pct:.1f}%**. "
                    + ("Target advertising schedules towards mid-week shoppers." if weekend_pct < 30 else "Weekend flash sales are yielding high returns.")
                )

    # ---- Tab 4: Natural Language Q&A ----
    with tabs[3]:
        section_title("Ask InsightIQ", "🤖")
        with card():
            st.caption("Ask questions about your sales data in plain English.")

            q_input = st.text_input(
                "Ask a question",
                placeholder="e.g., Which product category has the highest sales? What is our total profit?",
                label_visibility="collapsed",
                key="insight_user_question",
            )
            ask_btn = st.button("Ask InsightIQ", type="primary")

            if ask_btn and q_input:
                q = q_input.lower().strip()
                st.markdown("---")

                if "category" in q:
                    st.info(f"📊 **Category Performance:** **{top_cat}** is your top-selling category, generating **${cat_sales.iloc[0]:,.2f}** ({top_cat_share:.1f}% of total sales). The lowest category is **{cat_sales.index[-1]}** at **${cat_sales.iloc[-1]:,.2f}**.")
                elif "profit" in q or "margin" in q:
                    margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
                    st.info(f"💰 **Profit Summary:** Total profit across this dataset is **${total_profit:,.2f}**, representing an overall profit margin of **{margin:.1f}%**.")
                elif "region" in q or "city" in q or "state" in q:
                    st.info(f"🌍 **Regional Analysis:** **{top_region}** leads with **${top_region_sales:,.2f}** in revenue. All active regions: {', '.join([f'{r} (${s:,.0f})' for r, s in region_sales.items()])}.")
                elif "product" in q or "best" in q or "top" in q:
                    top_p = df.groupby("Product_Name")["Sales"].sum().idxmax()
                    top_p_sales = df.groupby("Product_Name")["Sales"].sum().max()
                    st.info(f"🏆 **Top Product:** Your #1 best-selling product is **'{top_p}'** with **${top_p_sales:,.2f}** in sales.")
                elif "discount" in q:
                    avg_disc = df["Discount"].mean() * 100
                    st.info(f"🏷️ **Discounting:** Average discount rate is **{avg_disc:.1f}%**. Full-price margins are **{full_margin:.1f}%** vs **{disc_margin:.1f}%** for discounted transactions.")
                elif "order" in q or "count" in q or "volume" in q:
                    st.info(f"🧾 **Orders:** You have **{len(df):,}** total orders in this dataset, with an Average Order Value of **${(total_sales / len(df)):,.2f}**.")
                else:
                    st.info(
                        f"📈 **Executive Summary:** Dataset has **{len(df):,}** orders totaling **${total_sales:,.2f}** in revenue and **${total_profit:,.2f}** in profit. "
                        f"Top category is **{top_cat}**, and leading region is **{top_region}**."
                    )
