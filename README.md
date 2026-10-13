# ⚽ Football Player Performance Analytics Dashboard

An interactive, portfolio-quality football (soccer) analytics dashboard built with
**Python**, **Streamlit**, **Pandas/NumPy**, and **Plotly**.

> ⚠️ **Data Disclaimer:** All player statistics in this application are **synthetic**
> (computer-generated using `numpy.random.seed(42)`). They are intended for
> demonstration purposes only and do **not** represent real-world football results
> or any actual player's performance.

---

## 📁 Project Structure

```
FOOTBALL/
├── app.py                  # Main Streamlit application (single file, modular functions)
├── football_players.csv    # Synthetic dataset — 864 rows, 21 columns, 3 seasons
├── generate_data.py        # Standalone script to regenerate the dataset
├── requirements.txt        # Python dependencies (pinned versions)
└── README.md               # This file
```

---

## 🚀 Features

| Page | What you get |
|---|---|
| **📊 Overview** | 5 KPI cards (players, goals, assists, minutes, avg rating) + Top-10 bar charts + searchable stats table + CSV download |
| **🧍 Player Analysis** | Multi-player comparison table · Goals vs Assists scatter · Shots vs Goals scatter with trendline · Rating violin plot |
| **🏟 Team Analysis** | Grouped goals/assists bar · Player count bar · Avg rating bar · Team summary table |
| **🎽 Position Analysis** | Avg stats grouped bar · Pass accuracy bar · Rating box plot · Card discipline stacked bar · Radar chart |

**Sidebar filters:** Season · Team · Position · Player name search (applied globally across all pages)

---

## 🛠 Setup & Run Locally

### Prerequisites

- Python 3.9 or higher
- `pip` (comes with Python)

### 1 — Clone or download the project

```bash
git clone https://github.com/your-username/football-dashboard.git
cd football-dashboard
```

### 2 — Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — (Optional) Regenerate the dataset

The CSV is already included. Run this only if you want a fresh copy:

```bash
python generate_data.py
```

### 5 — Launch the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at **http://localhost:8501**

---

## ☁️ Deploy to Streamlit Community Cloud

1. **Push your project** to a public GitHub repository (include all four files).
2. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** → select your repository and branch.
4. Set **Main file path** to `app.py`.
5. Click **Deploy** — your app will be live within a minute.

No extra configuration files are needed; Streamlit Cloud reads `requirements.txt` automatically.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥ 1.35.0 | Web app framework |
| `pandas` | ≥ 2.1.0 | Data manipulation |
| `numpy` | ≥ 1.26.0 | Numerical operations & random data generation |
| `plotly` | ≥ 5.22.0 | Interactive charts |

---

## 🗄 Dataset Schema

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique identifier per row |
| player_name | str | Synthetic full name |
| age | int | Age in years (17–38) |
| nationality | str | Country (synthetic pool) |
| team | str | Club name (12 synthetic clubs) |
| position | str | GK / DEF / MID / FWD |
| season | str | 2021-22, 2022-23, 2023-24 |
| matches_played | int | Matches played that season |
| minutes_played | int | Total minutes on pitch |
| goals | int | Goals scored |
| assists | int | Assists provided |
| shots | int | Total shots |
| shots_on_target | int | Shots on target |
| pass_accuracy | float | Pass completion rate (0–1) |
| key_passes | int | Passes leading to a shot |
| tackles | int | Successful tackles |
| interceptions | int | Ball interceptions |
| clean_sheets | int | Clean sheets (GK/DEF only) |
| yellow_cards | int | Yellow cards received |
| red_cards | int | Red cards received |
| rating | float | Composite performance score (5.0–9.5) |

---

## 📐 KPI & Rating Formula

All KPIs are calculated at runtime from the filtered dataset — nothing is hardcoded.

```
rating = 5.0
       + min(goals   × 0.15, 2.0)
       + min(assists × 0.10, 1.5)
       + pass_accuracy × 1.50
       + min(clean_sheets × 0.10, 1.0)   # GK / DEF only
       - yellow_cards × 0.05
       - red_cards    × 0.20
       + noise(μ=0, σ=0.15)
       clipped to [5.0, 9.5]
```

---

## 🎨 UI Theme

- Background: `#0d1117` (near-black)
- Surface cards: `#1a2332`
- Accent green: `#00ff87` (pitch green)
- Plotly template: `plotly_dark`

---

*Built as a portfolio project. All data is synthetic.*
