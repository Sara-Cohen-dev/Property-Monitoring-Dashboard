import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "property_monitoring.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Creating properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            apn TEXT PRIMARY KEY,
            address TEXT,
            total_units TEXT,
            regional_office TEXT
        )
    ''')
    
    # Creating cases table with composite key (number + type)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_number TEXT,
            apn TEXT,
            type TEXT,
            status TEXT,
            urgency TEXT,
            opened_date TEXT,
            deadline_date TEXT,
            closed_date TEXT,
            last_activity TEXT,
            nature TEXT,
            current_step TEXT,
            is_new INTEGER DEFAULT 0,
            PRIMARY KEY (case_number, type), 
            FOREIGN KEY (apn) REFERENCES properties (apn)
        )
    ''')
    conn.commit()
    conn.close()

def save_dashboard_data(apn, prop_info, cases_df):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Updating property data
    cursor.execute('''
        INSERT OR REPLACE INTO properties (apn, address, total_units, regional_office)
        VALUES (?, ?, ?, ?)
    ''', (
        apn, 
        prop_info.get('address'), 
        prop_info.get('total_units'), 
        prop_info.get('regional_office') 
    ))

    def to_str(val):
        if pd.isnull(val): return None
        # Saving in standard format that's easy to read later
        if hasattr(val, 'strftime'):
            return val.strftime('%Y-%m-%d %H:%M:%S')
        return str(val)

    # Updating cases - switching to snake_case
    for _, row in cases_df.iterrows():
        cursor.execute('''
            INSERT OR REPLACE INTO cases (
                case_number, apn, type, status, urgency,
                opened_date, deadline_date, closed_date, last_activity,
                nature, current_step, is_new
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(row['case_number']), 
            apn, 
            row['type'],             
            row['status'],          
            row['urgency'],          
            to_str(row['opened_date']), 
            to_str(row['deadline_date']), 
            to_str(row['closed_date']), 
            to_str(row['last_activity']), 
            row.get('nature', 'N/A'), 
            row.get('current_step', 'N/A'), 
            int(row['is_new'])
        ))
    
    conn.commit()
    conn.close()

def get_dashboard_data(apn):
    conn = sqlite3.connect(DB_NAME)
    # Safe loading with parameters
    prop_df = pd.read_sql("SELECT * FROM properties WHERE apn = ?", conn, params=(apn,))
    cases_df = pd.read_sql("SELECT * FROM cases WHERE apn = ?", conn, params=(apn,))
    conn.close()
    
    if prop_df.empty: 
        return None, pd.DataFrame()
    
    # Converting dates back to pandas objects
    date_cols = ['opened_date', 'deadline_date', 'closed_date', 'last_activity']
    for col in date_cols:
        if col in cases_df.columns:
            cases_df[col] = pd.to_datetime(cases_df[col], errors='coerce')
            
    # Converting property data to dictionary
    return prop_df.iloc[0].to_dict(), cases_df