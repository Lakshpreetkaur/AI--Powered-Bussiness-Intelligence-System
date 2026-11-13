# InsightIQ 📊

**AI Sales Business Intelligence Platform** — a modern Streamlit dashboard for uploading sales data, exploring KPIs, forecasting revenue with Machine Learning, and surfacing plain-English business insights.

---

## ✨ Features

- 🏠 **Home** — workspace snapshot, dynamic KPI summary, workflow shortcuts
- 📤 **Upload Dataset** — CSV/Excel drag-and-drop, automated schema validation, column mapping, feature engineering, and instant 1-click Demo Data loader
- 📊 **Interactive Dashboard** — dynamic revenue KPIs, date/region/category filters, and Plotly charts (monthly trend, sales by category, regional split, top 10 products)
- 🔮 **AI Sales Predictions** — powered by a pre-trained **Random Forest Regressor** pipeline; supports horizon forecasting and What-If deal pricing simulations
- 💡 **Business Insights** — plain-English recommendations on top drivers, pricing & discount sensitivity, fast/slow inventory alerts, seasonal trends, and natural-language Q&A
- 🔐 **Authentication** — SQLite user management with salted PBKDF2-HMAC-SHA256 password hashing
- 👤 **Profile** — live account details and workspace preferences

## 🎨 Design

- Dark navy blue SaaS dashboard theme with responsive cards
- Custom CSS (`assets/style.css`) — rounded cards, soft shadows, gradient accents
- `Poppins` for headings, `Inter` for body text
- Streamlit wide layout with custom sidebar navigation

## 🗂️ Project Structure

```
insightiq/
├── app.py                  # Entrypoint: page config, theme, navigation, auth gate
├── requirements.txt        # Streamlit, Pandas, Scikit-Learn 1.6.1, Joblib, Plotly, Openpyxl
├── README.md
├── assets/
│   └── style.css           # Global custom CSS theme
├── pages/                  # Modular screen controllers
│   ├── home.py             # Landing & snapshot
│   ├── dashboard.py        # Real-time KPIs & Plotly charts
│   ├── upload.py           # Ingestion, validation & demo dataset loader
│   ├── predictions.py      # ML model forecasting & What-If simulator
│   ├── insights.py         # AI business recommendations & Q&A
│   ├── profile.py          # Account info
│   ├── login.py            # Login form
│   └── signup.py           # Account creation form
├── utils/
│   ├── data.py             # Ingestion, cleaning, auto-mapping, and feature engineering
│   ├── styling.py          # load_css(), set_page_config()
│   ├── components.py       # KPI cards, page headers, feature tiles, etc.
│   ├── sidebar.py          # Sidebar brand header + footer + Logout
│   ├── database.py         # SQLite connection + users table CRUD
│   └── auth.py             # PBKDF2 password hashing & session management
├── insightiq.db            # SQLite database (auto-created on first run)
└── models/                 # Pre-trained ML pipelines
    ├── sales_prediction_pipeline.joblib   # Scikit-learn Pipeline (ColumnTransformer + Random Forest)
    └── sales_model_metadata.joblib       # Model metadata & feature definitions
```

## 🚀 Running Locally

```bash
# 1. Activate your virtual environment
.\venv\Scripts\activate          # Windows
source venv/bin/activate        # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## 🧪 Testing the App

1. Sign up or log into your account.
2. Navigate to **Upload Dataset**:
   - Click **"⚡ Load Demo Data"** to immediately test with 350 realistic retail transactions, OR
   - Click **"⬇️ Download Sample CSV"**, then drag-and-drop it into the uploader and click **"✅ Process Dataset"**.
3. Go to **Dashboard** to explore dynamic revenue, orders, margins, and filter by Region or Product Category.
4. Go to **Predictions** and click **"Run Forecast"** to run the Random Forest ML pipeline, or test the **What-If Order Value Simulator**.
5. Go to **Business Insights** to review automated executive recommendations and test the natural-language Q&A assistant.
