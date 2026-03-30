import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, GridUpdateMode, JsCode
import streamlit as st

# --- Cell coloring logic ---
cell_style_jscode = JsCode("""
function(params) {
    if (params.value === 'Critical') return {'color': 'white', 'background-color': '#ef4444', 'font-weight': 'bold'};
    if (params.value === 'Overdue') return {'color': 'white', 'background-color': '#f59e0b', 'font-weight': 'bold'};
    if (params.value === 'Safe') return {'color': 'white', 'background-color': '#10b981', 'font-weight': 'bold'};
    if (params.value === 'Active') return {'color': 'white', 'background-color': '#94a3b8'};
    return null;
}
""")

def render_table(data, key, cols_to_show, TYPE_EXPLANATIONS, search_query):
    if data.empty:
        st.info("No cases found for this filter.")
        return

    st.caption("💡 Click on a row to view full case details below.")

    work_df = data.copy()
    date_cols = ['opened_date', 'deadline_date', 'last_activity', 'closed_date']
    for c in date_cols:
        if c in work_df.columns:
            work_df[c] = pd.to_datetime(work_df[c]).dt.strftime('%m/%d/%Y').fillna("-")

    if search_query:
        mask = work_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        work_df = work_df[mask]
        if work_df.empty:
            st.info("No cases match your search.")
            return

    rename_map = {
        "case_number": "Case Number", "type": "Type", "status": "Status", 
        "closed_date": "Closed Date", "urgency": "Urgency", 
        "opened_date": "Opened", "deadline_date": "Deadline", "last_activity": "Update"
    }

    display_df = work_df.rename(columns=rename_map)
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection(selection_mode="single", use_checkbox=False)

    if "Urgency" in display_df.columns:
        gb.configure_column("Urgency", cellStyle=cell_style_jscode, width=120)

    nice_cols = [rename_map.get(c, c) for c in cols_to_show]
    for c in display_df.columns:
        gb.configure_column(c, hide=(c not in nice_cols))

    res = AgGrid(
        display_df, 
        gridOptions=gb.build(), 
        theme='alpine', 
        height=280,
        allow_unsafe_jscode=True,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        update_mode=GridUpdateMode.SELECTION_CHANGED, 
        key=key
    )

    sel = res.get('selected_rows')
    selected_row = None
    
    if sel is not None:
        if isinstance(sel, pd.DataFrame) and not sel.empty:
            selected_row = sel.iloc[0]
        elif isinstance(sel, list) and len(sel) > 0:
            selected_row = sel[0]

    if selected_row is not None:
        exp = TYPE_EXPLANATIONS.get(selected_row['Type'], "")
        
        st.markdown(f"""
        <div class="details-wrapper">
            <div style="font-weight:700; color:#1e3a8a; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;">
                Case # {selected_row['Case Number']} | {selected_row['Type']} 
                <span style="font-weight:400; color:#475569; margin-left:10px;">({exp})</span>
            </div>
            <div style="margin:10px 0; font-weight:500;">{selected_row.get('nature', 'N/A')}</div>
            <p style="margin:0;"><small><b>Status:</b> {selected_row.get('current_step', 'N/A')} | <b>Update:</b> {selected_row.get('Update', 'N/A')}</small></p>
        </div>
        """, unsafe_allow_html=True)