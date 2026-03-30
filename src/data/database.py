import logging
import sqlite3
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardRepository:
    """Repository for property and cases persistence."""

    def __init__(self, db_name: str = "property_monitoring.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        logger.info(f"Initializing database {self.db_name}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    apn TEXT PRIMARY KEY,
                    address TEXT,
                    total_units TEXT,
                    regional_office TEXT
                )
            ''')
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

    @staticmethod
    def _to_str(val):
        if pd.isnull(val):
            return None
        if hasattr(val, 'strftime'):
            return val.strftime('%Y-%m-%d %H:%M:%S')
        return str(val)

    def save_dashboard_data(self, apn, prop_info, cases_df: pd.DataFrame):
        logger.info(f"Saving dashboard data for APN {apn}")
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO properties (apn, address, total_units, regional_office)
                VALUES (?, ?, ?, ?)
            ''', (
                apn,
                prop_info.get('address'),
                prop_info.get('total_units'),
                prop_info.get('regional_office')
            ))

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
                    self._to_str(row['opened_date']),
                    self._to_str(row['deadline_date']),
                    self._to_str(row['closed_date']),
                    self._to_str(row['last_activity']),
                    row.get('nature', 'N/A'),
                    row.get('current_step', 'N/A'),
                    int(row['is_new'])
                ))
            conn.commit()

    def get_dashboard_data(self, apn):
        logger.info(f"Loading dashboard data for APN {apn}")
        with sqlite3.connect(self.db_name) as conn:
            prop_df = pd.read_sql("SELECT * FROM properties WHERE apn = ?", conn, params=(apn,))
            cases_df = pd.read_sql("SELECT * FROM cases WHERE apn = ?", conn, params=(apn,))

        if prop_df.empty:
            return None, pd.DataFrame()

        for col in ['opened_date', 'deadline_date', 'closed_date', 'last_activity']:
            if col in cases_df.columns:
                cases_df[col] = pd.to_datetime(cases_df[col], errors='coerce')

        return prop_df.iloc[0].to_dict(), cases_df
