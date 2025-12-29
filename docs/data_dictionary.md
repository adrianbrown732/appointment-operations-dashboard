# Appointments Data Dictionary

## Table: appointments.csv
**Grain:** one row per scheduled appointment event (including completed, canceled, no-show, rescheduled).

### Primary identifier
- **appointment_id**: intended unique appointment identifier (may include duplicates intentionally)

### Join keys (not unique)
- **patient_id**: pseudonymous patient identifier (multiple appointments per patient)
- **provider_id**: provider identifier (multiple appointments per provider)
- **clinic_id**: clinic identifier

### Timestamp conventions
All timestamps represent local clinic time. Fields may be missing depending on appointment status.

---

## Columns

### appointment_id
- Type: string
- Description: Appointment event identifier
- Notes: Duplicates may exist (intentional for dedup logic)

### patient_id
- Type: string
- Description: Pseudonymous patient identifier
- Notes: Not unique; used for grouping, not identification

### provider_id
- Type: string
- Description: Provider identifier

### clinic_id
- Type: string
- Description: Clinic/location identifier

### scheduled_start
- Type: datetime (string)
- Description: Scheduled start datetime for appointment
- Notes: May appear in mixed formats for a small subset of rows

### scheduled_end
- Type: datetime (string)
- Description: Scheduled end datetime for appointment

### created_at
- Type: datetime (string)
- Description: When the appointment was booked/created

### check_in_time
- Type: datetime (string, nullable)
- Description: Patient check-in time
- Notes: Often null for no-shows; may be missing due to data entry gaps

### visit_start_time
- Type: datetime (string, nullable)
- Description: Actual visit start time
- Notes: Usually present for completed visits; may be missing or illogical

### visit_end_time
- Type: datetime (string, nullable)
- Description: Actual visit end time
- Notes: May be missing; may be earlier than start in rare cases (intentional)

### canceled_at
- Type: datetime (string, nullable)
- Description: Timestamp when appointment was canceled
- Notes: Expected for canceled status, but may be missing or occur after scheduled_start (intentional)

### cancel_reason
- Type: string (nullable)
- Description: Categorical/free-text reason for cancellation/reschedule
- Notes: May be blank even when canceled/rescheduled

### status
- Type: string
- Description: Appointment outcome status
- Canonical targets (after cleaning): completed, canceled, no_show, rescheduled
- Notes: Raw data includes inconsistent casing/spelling (e.g., "CANCELLED", "No Show", "no-show")

### status_detail
- Type: string (nullable)
- Description: Additional status detail (e.g., arrived_late, late_cancel, early_cancel)
- Notes: Often blank

### follow_up_needed
- Type: boolean-like string
- Description: Indicates whether a follow-up is needed
- Notes: Raw encoding varies (Y/N, Yes/No, true/false, 1/0, blank)

### follow_up_scheduled
- Type: boolean-like string (nullable)
- Description: Indicates whether a follow-up was scheduled
- Notes: Raw encoding varies; may be missing

### appointment_type
- Type: string
- Description: Type of appointment (e.g., therapy, med_check, intake, follow_up)
- Notes: Raw values may include casing/spacing variants (e.g., "MED CHECK", "intake ")

### visit_modality
- Type: string
- Description: in_person or telehealth

### insurance_type
- Type: string
- Description: Insurance/payment category
- Canonical targets (after cleaning): medicaid, medicare, commercial, self_pay
- Notes: Raw values may include abbreviations/variants (e.g., "COMM", "self pay", "MCD")

### referral_source
- Type: string
- Description: Source of referral (self, primary_care, school, er, other)

### language
- Type: string
- Description: Patient preferred language category

### zip3
- Type: string
- Description: First 3 digits of ZIP code (privacy-preserving location)
- Notes: Expected 3 digits when present

### age_band
- Type: string
- Description: Patient age band (e.g., 25-34, 65+)

---

## Known Data Quality Issues (intentional)
- Mixed date formats for a small subset of timestamp fields
- Inconsistent status labels/casing (e.g., "No Show", "no-show", "NOSHOW")
- Boolean-like fields use inconsistent encodings and may be blank
- Missing timestamps (especially check-in / visit times)
- Occasional illogical timestamp ordering (e.g., visit_end_time earlier than visit_start_time)
- Occasional duplicate appointment_id values

