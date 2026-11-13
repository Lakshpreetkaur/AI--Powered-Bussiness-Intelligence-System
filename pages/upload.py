"""
pages/upload.py
----------------
Dataset upload and processing screen.
Ingests CSV or Excel sales data, validates schema, engineers features,
and populates the shared session state for Dashboards, Predictions, and Insights.
"""

import pandas as pd
import streamlit as st
from utils.components import page_header, section_title, card, pill
from utils import data


def _safe_preview(file_obj) -> pd.DataFrame:
    """Safe reader for preview that tries multiple encodings to prevent any byte-decode errors."""
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    name = getattr(file_obj, "name", "").lower()
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file_obj)

    for enc in ["utf-8", "utf-8-sig", "cp1252", "latin1", "iso-8859-1"]:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            return pd.read_csv(file_obj, encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue

    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    return pd.read_csv(file_obj, encoding="latin1", encoding_errors="replace")


def render() -> None:
    has_data = data.has_dataset()
    summary = data.get_summary()

    page_header(
        title="Upload Dataset",
        subtitle="Bring in your sales data to power the dashboard and predictions.",
        badge="Active Dataset Loaded" if has_data else "Step 1 of 3",
    )

    # Active dataset banner if already loaded
    if has_data:
        with card():
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            with c1:
                st.markdown(f"**Current Active Dataset:** `{summary.get('rows', 0):,} records` loaded")
                st.caption(f"Date range: {summary.get('date_min', 'N/A')} to {summary.get('date_max', 'N/A')}")
            with c2:
                st.metric("Total Revenue", f"${summary.get('total_sales', 0):,.2f}")
            with c3:
                st.metric("Avg Order Value", f"${summary.get('avg_order_value', 0):,.2f}")
            with c4:
                if st.button("🗑️ Clear Data", use_container_width=True, type="secondary"):
                    data.clear_dataset()
                    st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        with card():
            st.markdown("##### 📤 Drop your file here")
            uploaded_file = st.file_uploader(
                "Upload CSV or Excel file",
                type=["csv", "xlsx", "xls"],
                label_visibility="collapsed",
                key="sales_file_uploader",
            )
            st.caption("Supported formats: .csv, .xlsx, .xls  •  Max size: 200MB")

            b1, b2, b3 = st.columns([1, 1, 1])

            preview_clicked = False
            with b1:
                preview_clicked = st.button("🔍  Preview Data", use_container_width=True, type="secondary")
            with b2:
                process_clicked = st.button("✅  Process Dataset", use_container_width=True, type="primary")
            with b3:
                load_demo_clicked = st.button("⚡ Load Demo Data", use_container_width=True, help="Instantly load a realistic 350-row retail sales dataset")

            # Preview Action
            if preview_clicked:
                if uploaded_file is not None:
                    try:
                        preview_df = _safe_preview(uploaded_file)
                        st.markdown(f"**Previewing First 5 Rows:** `{len(preview_df):,} total rows, {len(preview_df.columns)} columns`")
                        st.dataframe(preview_df.head(5), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error reading file preview: {e}")
                else:
                    st.warning("Please select or drop a CSV/Excel file first, or click 'Load Demo Data'.")

            # Process Uploaded Action
            if process_clicked:
                if uploaded_file is not None:
                    with st.spinner("Processing dataset, engineering features, and preparing ML inputs..."):
                        try:
                            uploaded_file.seek(0)
                            raw_df, processed_df, summary = data.parse_and_process_file(uploaded_file)
                            data.save_dataset(raw_df, processed_df, summary)
                            st.success(f"🎉 Successfully processed {len(processed_df):,} records! Data is now live across the platform.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to process file: {e}")
                else:
                    st.warning("Please choose a file to process, or click 'Load Demo Data'.")

            # Load Demo Action
            if load_demo_clicked:
                with st.spinner("Generating demo sales dataset..."):
                    demo_raw = data.generate_sample_sales_data(350)
                    raw_df, processed_df, summary = data.parse_and_process_file(demo_raw)
                    data.save_dataset(raw_df, processed_df, summary)
                    st.success("🎉 Demo retail dataset loaded successfully! Check Dashboard and Predictions.")
                    st.rerun()

        section_title("Expected Columns", "🧩")
        with card():
            st.markdown(
                f"""
                {pill("Date", "blue")} {pill("Product Name", "blue")} {pill("Category", "blue")}
                {pill("Quantity", "blue")} {pill("Sales / Revenue", "blue")} {pill("Discount", "blue")}
                {pill("Region", "blue")} {pill("Ship Mode (optional)", "gray")}
                """,
                unsafe_allow_html=True,
            )
            st.caption("InsightIQ automatically normalizes column aliases and computes required dates, seasons, and shipping day features.")

    with col2:
        section_title("Upload Checklist", "✅")
        with card():
            st.markdown(
                f"""
                {pill("1. File is CSV or Excel", "green")}<br><br>
                {pill("2. Includes date & sales columns", "green")}<br><br>
                {pill("3. No merged header cells", "green")}<br><br>
                {pill("4. UTF-8 or standard encoding", "green")}
                """,
                unsafe_allow_html=True,
            )

        section_title("Need a sample?", "🗂️")
        with card():
            st.caption("Download a pre-structured sample sales CSV formatted for the AI models.")
            st.download_button(
                label="⬇️ Download Sample CSV",
                data=data.get_sample_csv_bytes(),
                file_name="insightiq_sample_sales.csv",
                mime="text/csv",
                use_container_width=True,
            )
