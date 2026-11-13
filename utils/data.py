"""
utils/data.py
-------------
Data ingestion, cleaning, validation, and feature-engineering pipeline
for InsightIQ. Prepares raw user uploads for visualization and ML model inference.
"""

from __future__ import annotations

import io
import random
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

DATASET_KEY = "insightiq_raw_data"
PROCESSED_KEY = "insightiq_processed_data"
SUMMARY_KEY = "insightiq_data_summary"

# Exact features expected by the trained Random Forest pipeline
REQUIRED_MODEL_FEATURES = [
    "Ship_Mode", "Segment", "Country/Region", "City", "State/Province",
    "Region", "Category", "Sub_Category", "Quantity", "Discount",
    "Order_Month", "Order_Year", "Order_Quarter", "Order_Day",
    "Order_Weekday", "Is_Weekend", "Shipping_Days"
]


# -----------------------------------------------------------------------------
# Column Auto-Mapping Dictionary
# -----------------------------------------------------------------------------
COLUMN_ALIASES = {
    "Order_Date": ["order date", "order_date", "date", "orderdate", "invoice_date", "transaction_date", "time"],
    "Ship_Date": ["ship date", "ship_date", "delivery_date", "shipping_date", "shipdate"],
    "Sales": ["sales", "revenue", "total_amount", "amount", "total_sales", "turnover", "price_total", "total"],
    "Quantity": ["quantity", "qty", "units", "units_sold", "volume", "count", "quantityordered", "quantity ordered"],
    "Discount": ["discount", "disc", "discount_rate", "discount_pct", "discount_percent"],
    "Profit": ["profit", "net_profit", "earnings", "margin"],
    "Category": ["category", "product_category", "department", "item_category", "productline", "product line"],
    "Sub_Category": ["sub-category", "sub_category", "subcategory", "sub category", "product_sub_category"],
    "Region": ["region", "zone", "territory", "area"],
    "State/Province": ["state/province", "state", "province", "state_province", "region_state"],
    "City": ["city", "town", "metro"],
    "Country/Region": ["country/region", "country", "nation"],
    "Segment": ["segment", "customer_segment", "client_segment", "market_segment", "dealsize", "deal size"],
    "Ship_Mode": ["ship mode", "ship_mode", "shipping_mode", "delivery_method", "shipping_method", "status"],
    "Product_Name": ["product name", "product_name", "product", "item_name", "item", "title", "productcode", "product code"],
    "Customer_Name": ["customer name", "customer_name", "customer", "client_name", "buyer"],
}


def _match_column(col_name: str) -> str | None:
    norm = col_name.strip().lower().replace("_", " ").replace("-", " ")
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            cleaned_alias = alias.lower().replace("_", " ").replace("-", " ")
            if norm == cleaned_alias:
                return canonical
    return None


# -----------------------------------------------------------------------------
# Robust Tabular Reader (Encodings & Formats)
# -----------------------------------------------------------------------------
def read_tabular_file(file_obj_or_df: Any) -> pd.DataFrame:
    """
    Reads a CSV or Excel file safely, handling UTF-8, UTF-8-BOM, CP1252/Windows-1252,
    Latin-1, and ISO-8859-1 encodings so byte-decode errors never occur.
    """
    if isinstance(file_obj_or_df, pd.DataFrame):
        return file_obj_or_df.copy()

    name = getattr(file_obj_or_df, "name", "").lower()
    if name.endswith((".xlsx", ".xls")):
        if hasattr(file_obj_or_df, "seek"):
            file_obj_or_df.seek(0)
        return pd.read_excel(file_obj_or_df)

    encodings_to_try = ["utf-8", "utf-8-sig", "cp1252", "latin1", "iso-8859-1"]
    for enc in encodings_to_try:
        try:
            if hasattr(file_obj_or_df, "seek"):
                file_obj_or_df.seek(0)
            return pd.read_csv(file_obj_or_df, encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue

    # Fallback with error replacement if non-standard characters exist
    if hasattr(file_obj_or_df, "seek"):
        file_obj_or_df.seek(0)
    return pd.read_csv(file_obj_or_df, encoding="latin1", encoding_errors="replace")


# -----------------------------------------------------------------------------
# Data Parser & Feature Engineer
# -----------------------------------------------------------------------------
def parse_and_process_file(file_obj_or_df: Any) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """
    Reads an uploaded CSV/Excel or existing DataFrame, normalizes columns,
    engineers date/shipping features required by the ML model, and computes summary metrics.
    """
    raw_df = read_tabular_file(file_obj_or_df)
    df = raw_df.copy()

    # Map detected columns
    col_mapping: dict[str, str] = {}
    for col in df.columns:
        matched = _match_column(str(col))
        if matched and matched not in col_mapping.values():
            col_mapping[col] = matched

    df = df.rename(columns=col_mapping)

    # 1. Date Handling
    if "Order_Date" in df.columns:
        df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    else:
        # Fallback date if missing: generate sequential dates over the last year
        df["Order_Date"] = pd.date_range(end=datetime.now(), periods=len(df), freq="D")

    # Fill NaT dates with median or today
    valid_dates = df["Order_Date"].dropna()
    fallback_date = valid_dates.iloc[0] if len(valid_dates) > 0 else pd.Timestamp.now()
    df["Order_Date"] = df["Order_Date"].fillna(fallback_date)

    if "Ship_Date" in df.columns:
        df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], errors="coerce")
        df["Ship_Date"] = df["Ship_Date"].fillna(df["Order_Date"] + pd.Timedelta(days=3))
    else:
        df["Ship_Date"] = df["Order_Date"] + pd.Timedelta(days=3)

    # 2. Date features (Required for ML model)
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Month"] = df["Order_Date"].dt.month
    df["Order_Quarter"] = df["Order_Date"].dt.quarter
    df["Order_Day"] = df["Order_Date"].dt.day
    df["Order_Weekday"] = df["Order_Date"].dt.weekday
    df["Is_Weekend"] = df["Order_Date"].dt.weekday.isin([5, 6]).astype(int)
    df["Shipping_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days.clip(lower=0).fillna(3).astype(int)

    # 3. Numeric Features
    if "Sales" in df.columns:
        df["Sales"] = pd.to_numeric(df["Sales"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0.0)
    else:
        df["Sales"] = 100.0

    if "Quantity" in df.columns:
        df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(1).astype(int)
    else:
        df["Quantity"] = 1

    if "Discount" in df.columns:
        df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce").fillna(0.0)
        # Normalize percentages > 1.0 down to 0-1 range
        df.loc[df["Discount"] > 1.0, "Discount"] = df["Discount"] / 100.0
    else:
        df["Discount"] = 0.0

    if "Profit" in df.columns:
        df["Profit"] = pd.to_numeric(df["Profit"].astype(str).str.replace(r"[^\d.-]", "", regex=True), errors="coerce").fillna(df["Sales"] * 0.2)
    else:
        df["Profit"] = df["Sales"] * 0.2

    # 4. Categorical Features with sensible defaults
    if "Category" not in df.columns:
        df["Category"] = "Technology"
    else:
        df["Category"] = df["Category"].fillna("Other").astype(str)

    if "Sub_Category" not in df.columns:
        df["Sub_Category"] = df["Category"]
    else:
        df["Sub_Category"] = df["Sub_Category"].fillna("General").astype(str)

    if "Region" not in df.columns:
        df["Region"] = "West"
    else:
        df["Region"] = df["Region"].fillna("Other").astype(str)

    if "State/Province" not in df.columns:
        df["State/Province"] = "California"
    else:
        df["State/Province"] = df["State/Province"].fillna("California").astype(str)

    if "City" not in df.columns:
        df["City"] = "Los Angeles"
    else:
        df["City"] = df["City"].fillna("Los Angeles").astype(str)

    if "Country/Region" not in df.columns:
        df["Country/Region"] = "United States"
    else:
        df["Country/Region"] = df["Country/Region"].fillna("United States").astype(str)

    if "Segment" not in df.columns:
        df["Segment"] = "Consumer"
    else:
        df["Segment"] = df["Segment"].fillna("Consumer").astype(str)

    if "Ship_Mode" not in df.columns:
        df["Ship_Mode"] = "Standard Class"
    else:
        df["Ship_Mode"] = df["Ship_Mode"].fillna("Standard Class").astype(str)

    if "Product_Name" not in df.columns:
        df["Product_Name"] = "Product " + df.index.astype(str)
    else:
        df["Product_Name"] = df["Product_Name"].fillna("Unknown Item").astype(str)

    # 5. Summary statistics
    total_sales = float(df["Sales"].sum())
    total_orders = len(df)
    avg_order_value = float(total_sales / total_orders) if total_orders > 0 else 0.0
    total_profit = float(df["Profit"].sum())
    profit_margin = float((total_profit / total_sales) * 100) if total_sales > 0 else 0.0

    min_date = df["Order_Date"].min().strftime("%Y-%m-%d") if not df.empty else "N/A"
    max_date = df["Order_Date"].max().strftime("%Y-%m-%d") if not df.empty else "N/A"

    summary = {
        "rows": total_orders,
        "columns": len(df.columns),
        "total_sales": total_sales,
        "total_orders": total_orders,
        "avg_order_value": avg_order_value,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "date_min": min_date,
        "date_max": max_date,
        "categories": sorted(df["Category"].unique().tolist()),
        "regions": sorted(df["Region"].unique().tolist()),
    }

    return raw_df, df, summary


# -----------------------------------------------------------------------------
# Extract Exact ML Features for Pipeline
# -----------------------------------------------------------------------------
def get_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts only the columns required by models/sales_prediction_pipeline.joblib."""
    for feat in REQUIRED_MODEL_FEATURES:
        if feat not in df.columns:
            if feat in ["Quantity", "Discount", "Order_Month", "Order_Year", "Order_Quarter", "Order_Day", "Order_Weekday", "Is_Weekend", "Shipping_Days"]:
                df[feat] = 0
            else:
                df[feat] = "Unknown"

    return df[REQUIRED_MODEL_FEATURES].copy()


# -----------------------------------------------------------------------------
# Demo / Sample Data Generator
# -----------------------------------------------------------------------------
def generate_sample_sales_data(n_rows: int = 350) -> pd.DataFrame:
    """Generates realistic sales transactions perfectly compatible with the platform and ML model."""
    random.seed(42)
    np.random.seed(42)

    categories = {
        "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
        "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "Office Supplies": ["Storage", "Binders", "Appliances", "Paper", "Art"]
    }
    regions = {
        "West": [("California", "Los Angeles"), ("California", "San Francisco"), ("Washington", "Seattle")],
        "East": [("New York", "New York City"), ("Pennsylvania", "Philadelphia"), ("Massachusetts", "Boston")],
        "Central": [("Illinois", "Chicago"), ("Texas", "Houston"), ("Texas", "Dallas")],
        "South": [("Florida", "Miami"), ("North Carolina", "Charlotte"), ("Georgia", "Atlanta")]
    }
    segments = ["Consumer", "Corporate", "Home Office"]
    ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

    base_date = datetime.now() - timedelta(days=365)
    rows = []

    for i in range(1, n_rows + 1):
        order_date = base_date + timedelta(days=random.randint(0, 360))
        shipping_days = random.choices([1, 2, 3, 5, 7], weights=[10, 20, 45, 15, 10])[0]
        ship_date = order_date + timedelta(days=shipping_days)

        category = random.choice(list(categories.keys()))
        sub_cat = random.choice(categories[category])
        region = random.choice(list(regions.keys()))
        state, city = random.choice(regions[region])
        segment = random.choices(segments, weights=[50, 30, 20])[0]
        ship_mode = random.choices(ship_modes, weights=[60, 20, 15, 5])[0]

        quantity = random.randint(1, 10)
        discount = random.choices([0.0, 0.1, 0.2, 0.3, 0.5], weights=[60, 15, 15, 7, 3])[0]

        base_unit_price = {
            "Technology": random.uniform(150, 950),
            "Furniture": random.uniform(80, 500),
            "Office Supplies": random.uniform(15, 120),
        }[category]

        sales = round(quantity * base_unit_price * (1 - discount), 2)
        profit_margin = random.uniform(0.1, 0.35) if discount <= 0.2 else random.uniform(-0.15, 0.05)
        profit = round(sales * profit_margin, 2)

        rows.append({
            "Order ID": f"CA-2024-{100000 + i}",
            "Order Date": order_date.strftime("%Y-%m-%d"),
            "Ship Date": ship_date.strftime("%Y-%m-%d"),
            "Ship Mode": ship_mode,
            "Customer ID": f"CUST-{random.randint(100, 300)}",
            "Customer Name": f"Customer {random.randint(1, 150)}",
            "Segment": segment,
            "Country/Region": "United States",
            "City": city,
            "State/Province": state,
            "Region": region,
            "Product ID": f"PROD-{sub_cat[:3].upper()}-{random.randint(100, 999)}",
            "Category": category,
            "Sub-Category": sub_cat,
            "Product Name": f"{sub_cat} Pro {random.randint(10, 99)}",
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit,
        })

    return pd.DataFrame(rows)


def get_sample_csv_bytes() -> bytes:
    df = generate_sample_sales_data(250)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


# -----------------------------------------------------------------------------
# Session State Helpers
# -----------------------------------------------------------------------------
def has_dataset() -> bool:
    return PROCESSED_KEY in st.session_state and isinstance(st.session_state[PROCESSED_KEY], pd.DataFrame) and not st.session_state[PROCESSED_KEY].empty


def get_dataset() -> pd.DataFrame | None:
    if has_dataset():
        return st.session_state[PROCESSED_KEY]
    return None


def get_raw_dataset() -> pd.DataFrame | None:
    if DATASET_KEY in st.session_state and isinstance(st.session_state[DATASET_KEY], pd.DataFrame):
        return st.session_state[DATASET_KEY]
    return None


def get_summary() -> dict[str, Any]:
    return st.session_state.get(SUMMARY_KEY, {})


def save_dataset(raw_df: pd.DataFrame, processed_df: pd.DataFrame, summary: dict[str, Any]) -> None:
    st.session_state[DATASET_KEY] = raw_df
    st.session_state[PROCESSED_KEY] = processed_df
    st.session_state[SUMMARY_KEY] = summary


def clear_dataset() -> None:
    for key in [DATASET_KEY, PROCESSED_KEY, SUMMARY_KEY]:
        if key in st.session_state:
            del st.session_state[key]

