import json
import os
import streamlit as st
from src.data.database import DashboardRepository
from src.data.processor import enrich_cases
from src.data.scraper import LAHDScraper
from src.ui.ui_utils import render_table
import pandas as pd

# --- Page Settings ---
st.set_page_config(page_title="LA Property Monitor", layout="wide", page_icon="🏠")

# Layer instances
repository = DashboardRepository()
scraper = LAHDScraper()

# Type explanations loaded from JSON config
def load_type_explanations() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'type_explanations.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

TYPE_EXPLANATIONS = load_type_explanations()

# --- CSS styling ---
st.markdown("""
<style>
.block-container { padding-top: 1rem; }
.side-info-box { padding: 12px; background-color: #f1f5f9; border-radius: 8px; border: 1px solid #cbd5e1; color: #0f172a; }
.details-wrapper { background: #f8fafc; padding: 15px; border-radius: 10px; border: 2px solid #e2e8f0; margin-top: 15px; color: #0f172a; }
.ag-theme-alpine { --ag-selected-row-background-color: #f1f5f9 !important; }
.ag-theme-alpine .ag-cell { display: flex; align-items: center; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("Search Property")
    apn = st.text_input("Property APN:", value="2654002037")
    if st.button("Refresh Data", use_container_width=True):
        with st.spinner("Loading..."):
            prop, cases = scraper.scrape_lahd_data(apn)
            if prop:
                cases_df = pd.DataFrame(cases)
                if not cases_df.empty:
                    cases_df = enrich_cases(cases_df)
                repository.save_dashboard_data(apn, prop, cases_df)
    
    prop_info, df = repository.get_dashboard_data(apn)
    if not df.empty:
        df = enrich_cases(df)

    if prop_info:
        st.markdown(f"""<div class="side-info-box">
            <b>Address:</b> {prop_info["address"]}<br>
            <b>Units:</b> {prop_info["total_units"]}<br>
            <b>Office:</b> {prop_info["regional_office"]}
        </div>""", unsafe_allow_html=True)

# --- Main ---
st.title("🏠 Property Monitoring Dashboard")

if prop_info:
    open_df = df[df['status'] == 'Open']
    urg_df = df[(df['status'] == 'Open') & (df['urgency'] == 'Critical')]
    new_df = df[df['is_new'] == 1]
    hist_df = df[df['status'] == 'Closed']

    if not urg_df.empty:
        st.markdown('<div style="background-color: #fee2e2; border: 1px solid #fecaca; color: #dc2626; padding: 3px 6px; border-radius: 4px; margin-bottom: 10px; font-size: 0.8em; display: inline-block; width: fit-content;">⚠ Critical issues detected</div>', unsafe_allow_html=True)

    col_m, col_s = st.columns([3, 1])
    with col_m:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df)); m2.metric("Open", len(open_df))
        m3.metric("Urgent", len(urg_df) if len(urg_df) > 0 else None)
        m4.metric("New", len(new_df))
    
    search_query = col_s.text_input("", placeholder="🔍 Search...", label_visibility="collapsed")

    tabs = st.tabs(["📋 All", "🔓 Open", "🚨 Urgent", "✨ New", "📁 History"])
    with tabs[0]: render_table(df, "t1", ["case_number", "type", "opened_date", "urgency"], TYPE_EXPLANATIONS, search_query)
    with tabs[1]: render_table(open_df, "t2", ["case_number", "type", "deadline_date", "urgency"], TYPE_EXPLANATIONS, search_query)
    with tabs[2]: render_table(urg_df, "t3", ["case_number", "type", "deadline_date", "urgency"], TYPE_EXPLANATIONS, search_query)
    with tabs[3]: render_table(new_df, "t4", ["case_number", "type", "opened_date", "urgency"], TYPE_EXPLANATIONS, search_query)
    with tabs[4]: render_table(hist_df, "t5", ["case_number", "type", "closed_date"], TYPE_EXPLANATIONS, search_query)
else:
    st.info("Enter APN in sidebar.")