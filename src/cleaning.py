"""
Cleaning and feature engineering utilities for appointment operations data.

This module converts raw, messy inputs into a consistent, analysis-ready dataset
while intentionally preserving operational edge cases.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd


# ----------------------------
# Canonical categories (the contract)
# ----------------------------

CANON_STATUS = {"completed", "canceled", "no_show", "rescheduled"}
CANON_APPOINTMENT_TYPE = {"therapy", "med_check", "intake", "follow_up"}
CANON_INSURANCE_TYPE = {"medicaid", "medicare", "commercial", "self_pay"}
CANON_MODALITY = {"in_person", "telehealth"}


# ----------------------------
# Normalization helpers
# ----------------------------

def _norm_text(raw_text: object) -> str:
    """Normalize text for matching: lower, strip, collapse spaces, replace hyphens."""
    if pd.isna(raw_text):
        return ""
    proc_text = str(raw_text).strip().lower()
    proc_text = proc_text.replace("-", " ")
    proc_text = " ".join(proc_text.split())
    return proc_text


def parse_boolish(raw_text: object) -> Optional[bool]:
    """
    Parse common boolean-like encodings to True/False.
    Returns None for missing/unknown.
    """
    proc_text = _norm_text(raw_text)
    if proc_text == "":
        return None

    truthy = {"true", "t", "yes", "y", "1"}
    falsy = {"false", "f", "no", "n", "0"}

    if proc_text in truthy:
        return True
    if proc_text in falsy:
        return False
    return None


# ----------------------------
# Category mappings (messy -> canonical)
# ----------------------------

STATUS_MAP = {
    # completed
    "completed": "completed",
    # canceled
    "canceled": "canceled",
    "cancelled": "canceled",
    # no show
    "no show": "no_show",
    "no_show": "no_show",
    "noshow": "no_show",
    "no-show": "no_show",
    # rescheduled
    "rescheduled": "rescheduled",
    "reschedule": "rescheduled",
}

APPOINTMENT_TYPE_MAP = {
    #therapy
    "therapy": "therapy",
    #med_check
    "med check": "med_check",
    "med_check": "med_check",
    "medcheck": "med_check",
    "med-check": "med_check",
    #intake
    "intake": "intake",
    #follow_up
    "follow up": "follow_up",
    "follow_up": "follow_up",
    "follow-up": "follow_up",
}

INSURANCE_TYPE_MAP = {
    #medicaid
    "medicaid": "medicaid",
    "mcd": "medicaid",
    #medicare
    "medicare": "medicare",
    "mcr": "medicare",
    #commercial
    "commercial": "commercial",
    "comm": "commercial",
    "private": "commercial",
    #self_pay
    "self pay": "self_pay",
    "self_pay": "self_pay",
}

DATETIME_COLUMNS = [
    "scheduled_start",
    "scheduled_end",
    "created_at",
    "check_in_time",
    "visit_start_time",
    "visit_end_time",
    "canceled_at",
]

def map_category(value: object, mapping: dict[str, str]) -> Optional[str]:
    """
    Map a raw categorical value to a canonical value using the provided mapping.
    Returns None if missing/unknown.
    """
    s = _norm_text(value)
    if s == "":
        return None
    return mapping.get(s)


def summarize_unexpected(series: pd.Series, allowed: set[str]) -> set[str]:
    """
    Return the set of observed non-null values not in the allowed set.
    Intended for debugging/logging, not for raising exceptions yet.
    """
    observed = {unexpected_value for unexpected_value in series.dropna().astype(str)}
    return observed - allowed

def coerce_datetimes(df: pd.DataFrame, cols: list[str] = DATETIME_COLUMNS) -> pd.DataFrame:
    """
    Coerce datetime-like columns to pandas datetime.

    - Uses errors='coerce' so invalid parses become NaT (missing)
    - Works with mixed formats (e.g., 'YYYY-mm-dd HH:MM:SS' and 'mm/dd/YYYY HH:MM')
    - Does not drop rows
    """
    out = df.copy()

    for col in cols:
        if col not in out.columns:
            continue
        out[col] = pd.to_datetime(out[col], errors="coerce")

    return out

def clean_appointments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw appointments data into a consistent, analysis-ready shape.

    This stage:
    - Coerces datetime columns
    - Normalizes categorical columns to canonical vocabularies
    - Parses boolean-like fields to True/False/None

    This stage intentionally does NOT:
    - drop rows (except optional dedup in a later step)
    - compute derived metrics (lead/wait/duration)
    """
    out = df.copy()

    # 1) Coerce datetime columns
    out = coerce_datetimes(out)

    # 2) Normalize categorical fields using explicit mappings
    if "status" in out.columns:
        out["status"] = out["status"].map(lambda x: map_category(x, STATUS_MAP))

    if "appointment_type" in out.columns:
        out["appointment_type"] = out["appointment_type"].map(
            lambda x: map_category(x, APPOINTMENT_TYPE_MAP)
        )

    if "insurance_type" in out.columns:
        out["insurance_type"] = out["insurance_type"].map(
            lambda x: map_category(x, INSURANCE_TYPE_MAP)
        )

    # 3) Normalize modality (already clean in generator, but keeping explicit)
    if "visit_modality" in out.columns:
        out["visit_modality"] = out["visit_modality"].map(lambda x: map_category(x, {
            "in_person": "in_person",
            "telehealth": "telehealth",
        }))

    # 4) Parse boolean-like fields
    for c in ["follow_up_needed", "follow_up_scheduled"]:
        if c in out.columns:
            out[c] = out[c].map(parse_boolish)

    # 5) Deduplicate on appointment_id (keep latest created_at)
    out = dedupe_latest_created_at(out)

    # 6) Derived time features (minutes)
    out = add_time_features(out)

    return out

def dedupe_latest_created_at(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate on appointment_id, keeping the row with the latest created_at.

    Assumes created_at has already been coerced to datetime.
    Rows with NaT created_at will sort last.
    """
    if "appointment_id" not in df.columns:
        return df

    out = df.copy()

    # Sort so the "latest created_at" is last within each appointment_id group
    if "created_at" in out.columns:
        out = out.sort_values(["appointment_id", "created_at"], na_position="first")
    else:
        out = out.sort_values(["appointment_id"])

    out = out.drop_duplicates(subset=["appointment_id"], keep="last")
    return out


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived time features in minutes.
    Assumes datetime columns have already been coerced.
    """
    out = df.copy()

    def minutes(delta):
        # pandas timedeltas support .dt.total_seconds()
        return delta.dt.total_seconds() / 60

    # Lead time: scheduled_start - created_at
    if {"scheduled_start", "created_at"} <= set(out.columns):
        out["lead_time_minutes"] = minutes(out["scheduled_start"] - out["created_at"])

    # Wait time: visit_start_time - scheduled_start
    if {"visit_start_time", "scheduled_start"} <= set(out.columns):
        out["wait_time_minutes"] = minutes(out["visit_start_time"] - out["scheduled_start"])

    # Visit duration: visit_end_time - visit_start_time
    if {"visit_end_time", "visit_start_time"} <= set(out.columns):
        out["visit_duration_minutes"] = minutes(out["visit_end_time"] - out["visit_start_time"])

    return out

def write_processed(df: pd.DataFrame, path: str) -> None:
    """
    Write cleaned appointments dataset to disk.
    Intended for local / downstream consumption (not committed).
    """
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if path.endswith(".parquet"):
        df.to_parquet(path, index=False)
    elif path.endswith(".csv"):
        df.to_csv(path, index=False)
    else:
        raise ValueError("Unsupported output format")
