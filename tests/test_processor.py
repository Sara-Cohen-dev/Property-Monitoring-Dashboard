import pytest
import pandas as pd
from src.data.processor import enrich_cases

def test_calculate_urgency_overdue():
    df = pd.DataFrame({
        "case_number": ["C1"],
        "type": ["Inspection"],
        "status": ["Open"],
        "opened_date": [pd.Timestamp("2023-01-01")],
        "deadline_date": [pd.Timestamp("2023-01-01")],
        "last_activity": [pd.Timestamp("2023-01-01")] 
    })
    result = enrich_cases(df)
    assert result.iloc[0]["urgency"] == "Overdue"

def test_calculate_urgency_future():
    df = pd.DataFrame({
        "case_number": ["C2"],
        "type": ["Complaint"],
        "status": ["Open"],
        "opened_date": [pd.Timestamp("2023-01-01")],
        "deadline_date": [pd.Timestamp("2099-01-01")],
        "last_activity": [pd.Timestamp("2023-01-01")] 
    })
    result = enrich_cases(df)
    assert result.iloc[0]["urgency"] == "Active"

def test_new_case_flag():
    df = pd.DataFrame({
        "case_number": ["C3"],
        "type": ["Complaint"],
        "status": ["Open"],
        "opened_date": [pd.Timestamp.now()],
        "deadline_date": [None],
        "last_activity": [pd.Timestamp.now()]
    })
    df = enrich_cases(df)
    assert df.iloc[0]["is_new"] == 1