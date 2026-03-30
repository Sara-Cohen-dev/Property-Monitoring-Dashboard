import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.processor import enrich_cases

def test_apply_business_logic():
    future_date = datetime.now() + timedelta(days=30)
    past_opened_date = datetime.now() - timedelta(days=5)

    # Sample data
    df = pd.DataFrame({
        "case_number": ["C001", "C002", "C003", "C004"],
        "type": ["Emergency", "Complaint", "Hearing", "REAP"],
        "status": ["Open", "Open", "Closed", "Open"],
        "opened_date": [past_opened_date] * 4,
        "deadline_date": [future_date, future_date, None, future_date],
        "last_activity": [past_opened_date] * 4,
        "is_new": [0, 0, 0, 0]
    })

    result = enrich_cases(df)

    assert result.loc[result['case_number'] == 'C001', 'urgency'].values[0] == 'Critical'
    assert result.loc[result['case_number'] == 'C002', 'urgency'].values[0] == 'Active'
    assert result.loc[result['case_number'] == 'C003', 'urgency'].values[0] == 'Safe'
    assert result.loc[result['case_number'] == 'C004', 'urgency'].values[0] == 'Critical'

def test_apply_business_logic_empty():
    df = pd.DataFrame()
    result = enrich_cases(df)
    assert result.empty

def test_apply_business_logic_overdue():
    past_date = datetime.now() - timedelta(days=1)
    df = pd.DataFrame({
        "case_number": ["C001"],
        "type": ["Complaint"],
        "status": ["Open"],
        "opened_date": [datetime.now() - timedelta(days=10)],
        "deadline_date": [past_date],
        "last_activity": [datetime.now() - timedelta(days=5)],
        "is_new": [0]
    })

    result = enrich_cases(df)
    assert result.loc[0, 'urgency'] == 'Overdue'