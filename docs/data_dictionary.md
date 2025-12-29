# Appointments Data Dictionary          ← document title

## Table: appointments.csv               ← table-level section
Grain: one row per scheduled appointment

### appointment_id                       ← column-level entry
- Type: string
- Description: Unique appointment identifier

### patient_id
- Type: string
- Description: Pseudonymous patient identifier

## Known Data Quality Issues              ← peer section to "Table"
- Status values are inconsistent
- Some timestamps are missing
