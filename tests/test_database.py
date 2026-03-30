import pytest
import pandas as pd
import sqlite3
from src.data.database import DashboardRepository

@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / 'test_property_monitoring.db'
    return DashboardRepository(str(db_path))

def test_tables_exist(repo):
    conn = sqlite3.connect(repo.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    assert 'properties' in tables
    assert 'cases' in tables

def test_save_and_get_data(repo):
    apn = "111222333"
    prop_info = {"address": "1 Main St", "total_units": "5", "regional_office": "Office A"}
    cases_df = pd.DataFrame({
        "case_number": ["T001"],
        "type": ["Complaint"],
        "status": ["Open"],
        "urgency": ["Critical"],
        "opened_date": [pd.Timestamp("2023-01-01")],
        "deadline_date": [pd.Timestamp("2023-01-15")],
        "closed_date": [None],
        "last_activity": [pd.Timestamp("2023-01-10")],
        "nature": ["Plumbing"],
        "current_step": ["Step 1"],
        "is_new": [1]
    })
    repo.save_dashboard_data(apn, prop_info, cases_df)
    prop, df = repo.get_dashboard_data(apn)
    assert prop["address"] == "1 Main St"
    assert df.iloc[0]["case_number"] == "T001"

def test_save_duplicate_apn_updates(repo):
    apn = "222333444"
    prop_info1 = {"address": "First St", "total_units": "3", "regional_office": "Office X"}
    prop_info2 = {"address": "Second St", "total_units": "4", "regional_office": "Office Y"}
    cases_df = pd.DataFrame({
        "case_number": ["D001"],
        "type": ["Inspection"],
        "status": ["Open"],
        "urgency": ["Safe"],
        "opened_date": [pd.Timestamp("2023-02-01")],
        "deadline_date": [None],
        "closed_date": [None],
        "last_activity": [pd.Timestamp("2023-02-05")],
        "nature": ["Roof"],
        "current_step": ["Step 1"],
        "is_new": [0]
    })
    repo.save_dashboard_data(apn, prop_info1, cases_df)
    repo.save_dashboard_data(apn, prop_info2, cases_df)  # Update
    prop, _ = repo.get_dashboard_data(apn)
    assert prop["address"] == "Second St"  # Must update