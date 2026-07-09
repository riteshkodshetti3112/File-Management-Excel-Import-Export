"""
Module 5: CSV Import & Export

Requirements implemented:
 * UTF-8 encoding (reading and writing)
 * Header validation
 * Duplicate detection (by employee_id / email, both within the file and
   against existing DB records)
"""
import csv
import io
from datetime import datetime

from .models import Department, Employee

REQUIRED_HEADERS = [
    "Employee ID", "First Name", "Last Name", "Email", "Phone",
    "Department", "Designation", "Salary", "Joining Date",
]


def _parse_date(value):
    value = (value or '').strip()
    if not value:
        return None
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {value}")


def import_employees_csv(uploaded_file):
    """
    Parses a UTF-8 encoded CSV file of employees.
    Returns a summary dict: total_rows, created, failed, errors (list of {row, error}).
    Invalid / duplicate rows are skipped; valid rows are saved.
    """
    raw_bytes = uploaded_file.read()
    try:
        decoded = raw_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        return {
            "total_rows": 0, "created": 0, "failed": 0,
            "errors": [{"row": 0, "error": "File is not valid UTF-8 encoded text."}],
        }

    reader = csv.DictReader(io.StringIO(decoded))

    if not reader.fieldnames:
        return {"total_rows": 0, "created": 0, "failed": 0,
                "errors": [{"row": 0, "error": "CSV file has no header row."}]}

    missing_headers = [h for h in REQUIRED_HEADERS if h not in reader.fieldnames]
    if missing_headers:
        return {
            "total_rows": 0, "created": 0, "failed": 0,
            "errors": [{"row": 0, "error": f"Missing required headers: {', '.join(missing_headers)}"}],
        }

    seen_ids, seen_emails = set(), set()
    total_rows, created, failed = 0, 0, 0
    errors = []

    for idx, row in enumerate(reader, start=2):  # row 1 is the header
        total_rows += 1
        try:
            emp_id = (row.get("Employee ID") or '').strip()
            email = (row.get("Email") or '').strip().lower()

            if not emp_id or not email:
                raise ValueError("Employee ID and Email are required.")
            if emp_id in seen_ids or email in seen_emails:
                raise ValueError("Duplicate row within uploaded file.")
            if Employee.objects.filter(employee_id=emp_id).exists():
                raise ValueError(f"Employee ID '{emp_id}' already exists.")
            if Employee.objects.filter(email__iexact=email).exists():
                raise ValueError(f"Email '{email}' already exists.")

            department = None
            dept_name = (row.get("Department") or '').strip()
            if dept_name:
                department, _ = Department.objects.get_or_create(name=dept_name)

            Employee.objects.create(
                employee_id=emp_id,
                first_name=(row.get("First Name") or '').strip(),
                last_name=(row.get("Last Name") or '').strip(),
                email=email,
                phone=(row.get("Phone") or '').strip(),
                department=department,
                designation=(row.get("Designation") or '').strip(),
                salary=row.get("Salary") or 0,
                joining_date=_parse_date(row.get("Joining Date")),
            )
            seen_ids.add(emp_id)
            seen_emails.add(email)
            created += 1
        except Exception as exc:
            failed += 1
            errors.append({"row": idx, "error": str(exc)})

    return {"total_rows": total_rows, "created": created, "failed": failed, "errors": errors}


def export_employees_csv(queryset):
    """Returns a UTF-8 encoded CSV string (with BOM for Excel compatibility)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(REQUIRED_HEADERS + ["Status"])
    for emp in queryset:
        writer.writerow([
            emp.employee_id, emp.first_name, emp.last_name, emp.email, emp.phone,
            emp.department.name if emp.department else '', emp.designation,
            emp.salary, emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else '',
            emp.status,
        ])
    return '\ufeff' + buffer.getvalue()
