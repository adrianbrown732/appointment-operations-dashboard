from src.data_io import load_appointments


def test_load_appointments_runs():
    df = load_appointments("data/raw/appointments.csv")
    assert len(df) > 0
