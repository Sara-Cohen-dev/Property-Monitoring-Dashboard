import pandas as pd
from datetime import datetime

HIGH_RISK_TYPES = {"Emergency", "Legal", "REAP", "Hearing"}
URGENCY_RULES = {
    "Closed": "Safe",
    "Overdue": "Overdue",
    "Critical": "Critical",
    "Active": "Active"
}


def determine_urgency(row) -> str:
    """Determine urgency based on status, type, and deadline."""
    status = row.get("status")
    case_type = row.get("type")
    deadline = row.get("deadline_date")

    if status == "Closed":
        return URGENCY_RULES["Closed"]

    if case_type in HIGH_RISK_TYPES:
        return URGENCY_RULES["Critical"]

    if pd.isna(deadline):
        return URGENCY_RULES["Active"]

    if deadline < datetime.now():
        return URGENCY_RULES["Overdue"]

    return URGENCY_RULES["Active"]


def _normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in ["opened_date", "last_activity", "deadline_date", "closed_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _calc_is_new(opened_date) -> int:
    if pd.isna(opened_date):
        return 0
    delta = datetime.now() - opened_date
    return 1 if delta.days <= 14 else 0


def enrich_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Apply business logic and urgency classification to case records."""
    if df.empty:
        return df

    df = _normalize_dates(df)
    df["urgency"] = df.apply(determine_urgency, axis=1)
    df["is_new"] = df["opened_date"].apply(_calc_is_new)

    return df.sort_values(by=["case_number", "last_activity"], ascending=[False, False])

