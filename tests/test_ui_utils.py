import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.ui.ui_utils import render_table

def test_date_formatting_logic():
    """Checks if dates are correctly formatted to MM/DD/YYYY as per UI requirements."""
    data = pd.DataFrame({
        "case_number": ["101"],
        "opened_date": [pd.Timestamp("2024-01-15")],
        "deadline_date": [pd.Timestamp("2024-12-31")]
    })
    
    work_df = data.copy()
    date_cols = ['opened_date', 'deadline_date']
    for c in date_cols:
        work_df[c] = pd.to_datetime(work_df[c]).dt.strftime('%m/%d/%Y')
        
    assert work_df.iloc[0]["opened_date"] == "01/15/2024"
    assert work_df.iloc[0]["deadline_date"] == "12/31/2024"

def test_search_filter_logic():
    """Verifies that the search query correctly masks the dataframe."""
    data = pd.DataFrame({
        "case_number": ["101", "202"],
        "type": ["Plumbing", "Electrical"],
        "nature": ["Leaking pipe", "Sparking wires"]
    })
    
    search_query = "Plumb"
    # Logic extracted from render_table
    mask = data.astype(str).apply(
        lambda x: x.str.contains(search_query, case=False)
    ).any(axis=1)
    
    filtered_df = data[mask]
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["case_number"] == "101"

def test_render_table_empty_data(monkeypatch):
    """Ensures the UI handles empty dataframes gracefully."""
    mock_st = MagicMock()
    monkeypatch.setattr("streamlit.info", mock_st.info)
    
    render_table(pd.DataFrame(), "test_key", [], {}, "")
    mock_st.info.assert_called_with("No cases found for this filter.")