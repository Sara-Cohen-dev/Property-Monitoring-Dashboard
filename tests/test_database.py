import os
import tempfile
import pytest
import pandas as pd
import sqlite3
import src.database as db
from src.database import init_db, save_dashboard_data, get_dashboard_data

@pytest.fixture
def test_db():
    with tempfile.TemporaryDirectory() as d:
        db_path = os.path.join(d, 'test_property_monitoring.db')
        db.DB_NAME = db_path
        init_db()
        
        conn = sqlite3.connect(db_path)
        yield conn
        conn.close()

def test_init_tables(test_db):
    cursor = test_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    assert 'properties' in tables
    assert 'cases' in tables

def test_save_dashboard_data(test_db):
    apn = "123456789"
    prop_info = {
        "address": "123 Test St",
        "total_units": "10",
        "regional_office": "Test Office"
    }
    cases_df = pd.DataFrame({
        "case_number": ["C001", "C002"],
        "apn": [apn, apn],
        "type": ["Complaint", "Hearing"],
        "status": ["Open", "Closed"],
        "urgency": ["Critical", "Safe"],
        "opened_date": [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-02-01")],
        "deadline_date": [pd.Timestamp("2023-03-01"), None],
        "closed_date": [None, pd.Timestamp("2023-03-01")],
        "last_activity": [pd.Timestamp("2023-01-15"), pd.Timestamp("2023-02-15")],
        "nature": ["Test nature 1", "Test nature 2"],
        "current_step": ["Step 1", "Step 2"],
        "is_new": [1, 0]
    })

    save_dashboard_data(apn, prop_info, cases_df)

    cursor = test_db.cursor()
    cursor.execute("SELECT address, total_units FROM properties WHERE apn = ?", (apn,))
    prop_row = cursor.fetchone()
    assert prop_row == ("123 Test St", "10")

    cases = pd.read_sql("SELECT * FROM cases WHERE apn = ?", test_db, params=(apn,))
    assert len(cases) == 2
    assert "C001" in cases['case_number'].values

def test_get_dashboard_data(test_db):
    apn = "987654321"
    prop_info = {"address": "Main St", "total_units": "5", "regional_office": "North"}
    cases_df = pd.DataFrame({
        "case_number": ["C999"], "apn": [apn], "type": ["Inspection"],
        "status": ["Open"], "urgency": ["High"],
        "opened_date": ["2024-01-01"], "deadline_date": ["2024-02-01"],
        "closed_date": [None], "last_activity": ["2024-01-05"],
        "nature": ["Roof"], "current_step": ["Review"], "is_new": [0]
    })

    save_dashboard_data(apn, prop_info, cases_df)
    
    prop, df = get_dashboard_data(apn)
    
    assert prop["address"] == "Main St"
    assert len(df) == 1
    assert df.iloc[0]['case_number'] == "C999"

def test_get_dashboard_data_no_data(test_db):
    prop, df = get_dashboard_data("nonexistent")
    assert prop is None
    assert df.empty