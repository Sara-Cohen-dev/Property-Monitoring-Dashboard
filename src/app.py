import streamlit as st
import database as db
import processor
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, GridUpdateMode, JsCode

# --- Page Settings ---
st.set_page_config(page_title="LA Property Monitor", layout="wide", page_icon="🏠")

db.init_db()

# Short explanations dictionary for case types
TYPE_EXPLANATIONS = {
    "Complaint": "Initial violation report",
    "Systematic Code Enforcement Program": "Routine periodic inspection (SCEP)",
    "Case Management": "Active inspector monitoring",
    "Rent Escrow Account Program": "REAP: Rent diverted to escrow",
    "Hearing": "Formal administrative review",
    "Property Management Training Program": "PMTP: Owner training program",
    "Legal": "Referred to City Attorney",
    "Emergency": "Critical health/safety hazard",
    "Out Reach Case": "Tenant advocacy engagement"
}

# --- CSS for general styling and text alignment in table ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .side-info-box { padding: 12px; background-color: #f1f5f9; border-radius: 8px; border: 1px solid #cbd5e1; color: #0f172a; }
    .details-wrapper { background: #f8fafc; padding: 15px; border-radius: 10px; border: 2px solid #e2e8f0; margin-top: 15px; color: #0f172a; }
    .ag-theme-alpine { --ag-selected-row-background-color: #f1f5f9 !important; }
    /* יישור טקסט למרכז בתאי הטבלה */
    .ag-theme-alpine .ag-cell { display: flex; align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Cell coloring logic  ---
cell_style_jscode = JsCode("""
function(params) {
    if (params.value === 'Critical') return {'color': 'white', 'background-color': '#ef4444', 'font-weight': 'bold'};
    if (params.value === 'Overdue') return {'color': 'white', 'background-color': '#f59e0b', 'font-weight': 'bold'};
    if (params.value === 'Safe') return {'color': 'white', 'background-color': '#10b981', 'font-weight': 'bold'};
    if (params.value === 'Active') return {'color': 'white', 'background-color': '#94a3b8'};
    return null;
}
""")

# --- Sidebar ---
with st.sidebar:
    st.header("Search Property")
    apn = st.text_input("Property APN:", value="2654002037")
    if st.button("Refresh Data", use_container_width=True):
        with st.spinner("Loading..."):
            prop, cases = processor.scrape_lahd_data(apn)
            if prop: db.save_dashboard_data(apn, prop, cases)
    
    prop_info, df = db.get_dashboard_data(apn)
    if prop_info:
        st.markdown(f"""<div class="side-info-box">
            <b>Address:</b> {prop_info["address"]}<br>
            <b>Units:</b> {prop_info["total_units"]}<br>
            <b>Office:</b> {prop_info["regional_office"]}
        </div>""", unsafe_allow_html=True)

# --- Main ---
st.title("🏠 Property Monitoring Dashboard")

if prop_info:
    # Data segmentation
    open_df = df[df['status'] == 'Open']
    urg_df = df[(df['status'] == 'Open') & (df['urgency'] == 'Critical')]
    new_df = df[df['is_new'] == 1]
    hist_df = df[df['status'] == 'Closed']

    col_m, col_s = st.columns([3, 1])
    with col_m:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df)); m2.metric("Open", len(open_df))
        m3.metric("Urgent", len(urg_df) if len(urg_df) > 0 else None)
        m4.metric("New", len(new_df))
    
    search_query = col_s.text_input("", placeholder="🔍 Search...", label_visibility="collapsed")

    def render_table(data, key, cols_to_show):
        if data.empty: return st.info("No records.")

        st.caption("💡 Click on a row to view full case details below.")
        
        work_df = data.copy()
        for c in ['opened_date', 'deadline_date', 'last_activity', 'closed_date']:
            if c in work_df.columns: 
                work_df[c] = pd.to_datetime(work_df[c]).dt.strftime('%m/%d/%Y').fillna("-")

        if search_query:
            mask = work_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
            work_df = work_df[mask]
            if work_df.empty: return st.info("No matches.")

        rename_map = {"case_number": "Case Number", "type": "Type", "status": "Status", "closed_date": "Closed Date",
                      "urgency": "Urgency", "opened_date": "Opened", "deadline_date": "Deadline", "last_activity": "Update"}
        
        display_df = work_df.rename(columns=rename_map)

        gb = GridOptionsBuilder.from_dataframe(display_df)
        gb.configure_selection(selection_mode="single")
        
        # Applying cell coloring to the Urgency column
        if "Urgency" in display_df.columns:
            gb.configure_column("Urgency", cellStyle=cell_style_jscode, width=120)

        # Selecting columns to display
        nice_cols = [rename_map.get(c, c) for c in cols_to_show]
        for c in display_df.columns:
            gb.configure_column(c, hide=(c not in nice_cols))

        res = AgGrid(display_df, gridOptions=gb.build(), theme='alpine', height=280, 
                     allow_unsafe_jscode=True,
                     columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                     update_mode=GridUpdateMode.SELECTION_CHANGED, key=key)

        # Details box on click
        sel = res['selected_rows']
        if sel is not None and len(sel) > 0:
            row = sel.iloc[0] if isinstance(sel, pd.DataFrame) else sel[0]
            exp = TYPE_EXPLANATIONS.get(row['Type'], "")
            
            st.markdown(f"""<div class="details-wrapper">
                <div style="font-weight:700; color:#1e3a8a; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;">
                    Case # {row['Case Number']} | {row['Type']} <span style="font-weight:400; color:#475569; margin-left:10px;">({exp})</span>
                </div>
                <div style="margin:10px 0; font-weight:500;">{row.get('nature', 'N/A')}</div>
                <small><b>Status:</b> {row.get('current_step', 'N/A')} | <b>Update:</b> {row.get('Update', 'N/A')}</small>
            </div>""", unsafe_allow_html=True)

    # Tabs
    t = st.tabs(["📋 All", "🔓 Open", "🚨 Urgent", "✨ New", "📁 History"])
    with t[0]: render_table(df, "t1", ["case_number", "type", "opened_date", "urgency"])
    with t[1]: render_table(open_df, "t2", ["case_number", "type", "deadline_date", "urgency"])
    with t[2]: render_table(urg_df, "t3", ["case_number", "type", "deadline_date", "urgency"])
    with t[3]: render_table(new_df, "t4", ["case_number", "type", "opened_date", "urgency"])
    with t[4]: render_table(hist_df, "t5", ["case_number", "type", "closed_date"])
else:
    st.info("Enter APN in sidebar.")