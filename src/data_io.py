from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = {
    "appointment_id",
    "patient_id",
    "provider_id",
    "clinic_id",
    "scheduled_start",
    "scheduled_end",
    "created_at",
    "check_in_time",
    "visit_start_time",
    "visit_end_time",
    "canceled_at",
    "cancel_reason",
    "status",
    "status_detail",
    "follow_up_needed",
    "follow_up_scheduled",
    "appointment_type",
    "visit_modality",
    "insurance_type",
    "referral_source",
    "language",
    "zip3",
    "age_band",
}


def load_appointments(path: str | Path) -> pd.DataFrame:
    """
    Load raw appointments data from CSV and perform basic schema validation.

    This function intentionally does NOT clean or transform values.
    It only ensures the dataset can be loaded and has the expected structure.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Appointments file not found: {path}")

    df = pd.read_csv(path)

    # Basic shape logging
    if df.empty:
        raise ValueError("Appointments dataset is empty")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df
