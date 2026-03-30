import pytest
import pandas as pd
import sqlite3
from src.data.database import DashboardRepository

@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / 'test_property_monitoring.db'
    repository = DashboardRepository(str(db_path))
    return repository


def test_init_tables(repo):
    conn = sqlite3.connect(repo.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()

    assert 'properties' in tables
    assert 'cases' in tables


def test_save_dashboard_data(repo):
    apn = "123456789"
    prop_info = {
        "address": "123 Test St",
        "total_units": "10",
        "regional_office": "Test Office"
    }
    cases_df = pd.DataFrame({
        "case_number": ["C001", "C002"],
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

    repo.save_dashboard_data(apn, prop_info, cases_df)

    conn = sqlite3.connect(repo.db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT address, total_units FROM properties WHERE apn = ?", (apn,))
    prop_row = cursor.fetchone()
    conn.close()

    assert prop_row == ("123 Test St", "10")

    conn = sqlite3.connect(repo.db_name)
    cases = pd.read_sql("SELECT * FROM cases WHERE apn = ?", conn, params=(apn,))
    conn.close()
    assert len(cases) == 2
    assert "C001" in cases['case_number'].values


def test_get_dashboard_data(repo):
    apn = "987654321"
    prop_info = {"address": "Main St", "total_units": "5", "regional_office": "North"}
    cases_df = pd.DataFrame({
        "case_number": ["C999"],
        "type": ["Inspection"],
        "status": ["Open"],
        "urgency": ["High"],
        "opened_date": ["2024-01-01"],
        "deadline_date": ["2024-02-01"],
        "closed_date": [None],
        "last_activity": ["2024-01-05"],
        "nature": ["Roof"],
        "current_step": ["Review"],
        "is_new": [0]
    })

    repo.save_dashboard_data(apn, prop_info, cases_df)

    prop, df = repo.get_dashboard_data(apn)

    assert prop["address"] == "Main St"
    assert len(df) == 1
    assert df.iloc[0]['case_number'] == "C999"


def test_get_dashboard_data_no_data(repo):
    prop, df = repo.get_dashboard_data("nonexistent")
    assert prop is None
    assert df.empty