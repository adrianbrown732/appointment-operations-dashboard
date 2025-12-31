import pandas as pd

from src.data_io import load_appointments
from src.cleaning import (
    clean_appointments,
    CANON_STATUS,
    CANON_APPOINTMENT_TYPE,
    CANON_INSURANCE_TYPE,
)

DATA_PATH = "data/raw/appointments.csv"


def test_clean_appointments_preserves_columns_and_adds_features():
    df_raw = load_appointments(DATA_PATH)
    df_clean = clean_appointments(df_raw)

    # Core original columns should remain present
    for col in ["appointment_id", "scheduled_start", "created_at", "status"]:
        assert col in df_clean.columns

    # Derived features should exist after Step 5
    for col in ["lead_time_minutes", "wait_time_minutes", "visit_duration_minutes"]:
        assert col in df_clean.columns


def test_clean_appointments_dedupes_on_appointment_id():
    df_raw = load_appointments(DATA_PATH)
    df_clean = clean_appointments(df_raw)

    assert df_clean["appointment_id"].isna().sum() == 0
    assert len(df_clean) == df_clean["appointment_id"].nunique()


def test_clean_appointments_status_is_canonical_or_null():
    df_raw = load_appointments(DATA_PATH)
    df_clean = clean_appointments(df_raw)

    observed = set(df_clean["status"].dropna().unique())
    assert observed <= CANON_STATUS


def test_clean_appointments_types_and_insurance_are_canonical_or_null():
    df_raw = load_appointments(DATA_PATH)
    df_clean = clean_appointments(df_raw)

    appt_obs = set(df_clean["appointment_type"].dropna().unique())
    ins_obs = set(df_clean["insurance_type"].dropna().unique())

    assert appt_obs <= CANON_APPOINTMENT_TYPE
    assert ins_obs <= CANON_INSURANCE_TYPE


def test_datetime_columns_are_datetime64():
    df_raw = load_appointments(DATA_PATH)
    df_clean = clean_appointments(df_raw)

    dt_cols = [
        "scheduled_start",
        "scheduled_end",
        "created_at",
        "check_in_time",
        "visit_start_time",
        "visit_end_time",
        "canceled_at",
    ]

    for col in dt_cols:
        assert pd.api.types.is_datetime64_any_dtype(df_clean[col]), f"{col} is not datetime"
