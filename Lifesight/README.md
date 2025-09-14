# 📊 Marketing Intelligence Dashboard

An interactive **Streamlit dashboard** to analyze marketing performance across **Facebook, Google, and TikTok** and connect it with business KPIs such as revenue, orders, and gross profit.  

This project was built as part of the Marketing Intelligence assignment.  

---

## 🚀 Features
- Load and clean multiple marketing data sources (Facebook, Google, TikTok).  
- Calculate key performance metrics: **CTR, CPC, CPM, ROAS**.  
- Merge marketing results with business outcomes (orders, revenue, profit).  
- Interactive dashboard with:
  - 📆 Date range filter  
  - 📺 Channel filter  
  - 💸 KPIs (Spend, Attributed Revenue, ROAS, Revenue Share)  
  - 📊 Time series (Spend vs Revenue vs Total Business Revenue)  
  - 🏆 Top campaigns table  
  - 🔎 Campaign drill-down analysis  
  - ⬇️ Export filtered dataset as CSV  

---

## 🛠️ Tech Stack
- [Python 3.10+](https://www.python.org/downloads/)  
- [Pandas](https://pandas.pydata.org/) – data cleaning and aggregation  
- [NumPy](https://numpy.org/) – calculations  
- [Streamlit](https://streamlit.io/) – interactive dashboard  
- [Plotly](https://plotly.com/python/) – interactive visualizations  

---

## 📂 Project Structure
marketing-dashboard/
│
├── data/ # Input CSV files
│ ├── Facebook.csv
│ ├── Google.csv
│ ├── TikTok.csv
│ └── Business.csv
│
├── app.py # Main Streamlit app
├── requirements.txt # Dependencies
└── README.md # Project documentation



---

## ⚡ Setup & Run

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/marketing-dashboard.git
   cd marketing-dashboard

2. Create and activate a virtual environment:

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


3. Install dependencies:

pip install -r requirements.txt


Place your data files in the data/ folder:

Facebook.csv

Google.csv

TikTok.csv

Business.csv

4. Run the dashboard:

streamlit run app.py


Open your browser at http://localhost:8501
 🎉


![alt text](<Screenshot (48).png>)

## 🔗 Live demo
- Live app: https://marketing-intelligence-dashboard-4u8pkyrdwf4rauch6n9htg.streamlit.app/