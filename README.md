# Appointment Operations Dashboard

Interactive dashboard for monitoring appointment outcomes (completed / canceled / no-show) and identifying operational patterns across clinics, providers, and appointment types.

## Problem Statement
Scheduling inefficiency and missed appointments reduce access to care and waste staff capacity. This project provides an interactive operations view that helps stakeholders identify where no-shows and cancellations concentrate and how timing factors (lead time, wait time) relate to outcomes.

## Data
Synthetic (realistic) appointment-level data with intentional quality issues for cleaning practice.

**Core table**
- `appointments.csv` (1 row = 1 scheduled appointment)

**Privacy notes**
- Patient identifiers are pseudonymous.
- Location is reduced to ZIP3 (first 3 digits).
- Age is stored as bands.

## Planned Metrics
- Appointment volume
- Completion rate, cancellation rate, no-show rate
- Median lead time (scheduled_start - created_at)
- Median wait time (visit_start_time - scheduled_start)
- Median visit duration (visit_end_time - visit_start_time)

## Planned Filters
- Date range (scheduled_start)
- Clinic
- Provider
- Appointment type
- Status

## Workflow
raw data → load/validate → clean/feature-engineer → processed dataset → dashboard
