# HRMS Document & Reporting Module — `company_portal`

A Django REST Framework project implementing all 12 modules of the HRMS
assignment: file uploads, document management, Excel/CSV import & export,
PDF generation (profile, salary slip, ID card), QR codes, reports, and a
dashboard — with role-based permissions (HR / Manager / Employee).

## 1. Setup (VS Code)

```bash
# 1. Open this folder in VS Code
# 2. Create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Seed the HR / Manager / Employee role groups
python manage.py seed_roles

# 6. Create an admin user
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` to manage data, or use the API at
`http://127.0.0.1:8000/api/v1/`.

Recommended VS Code extensions: **Python** (ms-python.python) and
**Pylance**. A `.vscode/settings.json` is intentionally not included —
point the Python interpreter at `./venv` after opening the folder.

## 2. Role-Based Access

Three Django Groups drive permissions (created by `seed_roles`):

| Group      | Can do                                                             |
|------------|---------------------------------------------------------------------|
| `HR`       | Full access: create/import/export employees, upload/delete any document, generate all reports |
| `Manager`  | Read-only on employees/reports; can view/download (not delete) any employee's documents |
| `Employee` | Can view their own employee record; upload/list/download **only their own** documents; cannot delete |

Link a `User` to an `Employee` via `Employee.user` (one-to-one) so an
"Employee" role account resolves to the correct record.

Authentication: Session auth (browsable API / `admin/`) or Token auth
(`rest_framework.authtoken` — obtain via `/api-auth/login/` or issue tokens
from the admin).

> **Note:** DRF reserves the query parameter `format` for content
> negotiation. All endpoints below use `file_format` (not `format`) to pick
> PDF / Excel / CSV.

## 3. Module → Endpoint Map

### Module 1 — File Uploads (Employee model)
`Employee` has `profile_photo` (JPG/PNG ≤5MB), `resume`, `aadhaar_document`,
`pan_document` (PDF ≤5MB). Enforced by validators in `employees/models.py`.

### Module 2 — Document Management
| Action   | Method & URL                                  |
|----------|------------------------------------------------|
| Upload   | `POST /api/v1/documents/`                      |
| List     | `GET /api/v1/documents/?employee=<id>`         |
| Retrieve | `GET /api/v1/documents/{id}/`                  |
| Delete   | `DELETE /api/v1/documents/{id}/`               |
| Download | `GET /api/v1/documents/{id}/download/`         |

### Module 3 — Excel Import
`POST /api/v1/employees/import/` — multipart field `file` (.xlsx). Returns:
```json
{"total_rows": 500, "created": 485, "failed": 15, "errors": [{"row": 12, "error": "..."}]}
```

### Module 4 — Excel Export
`GET /api/v1/employees/export/?type=employees|departments|salary|attendance`

### Module 5 — CSV Import & Export
- `POST /api/v1/employees/import-csv/` (multipart field `file`)
- `GET /api/v1/employees/export-csv/`

### Module 6 — Employee Profile PDF
`GET /api/v1/employees/{id}/profile-pdf/` → `EMP001_Profile.pdf`

### Module 7 — Salary Slip
`GET /api/v1/employees/{id}/salary-slip/?month=June&year=2026` → `SalarySlip_June_2026.pdf`

### Module 8 — QR Code
`GET /api/v1/employees/{id}/qr-code/` → PNG image (add `?save=true` to persist to `media/`)

### Module 9 — Employee ID Card
`GET /api/v1/employees/{id}/id-card/?valid_until=2027-01-01` → `ID_EMP001.pdf`

### Module 10 — Reports (Excel / PDF / CSV)
```
GET /api/v1/reports/employee/?file_format=pdf|excel|csv
GET /api/v1/reports/department/?file_format=...
GET /api/v1/reports/salary/?file_format=...
GET /api/v1/reports/attendance/?file_format=...
```

### Module 11 — File Download APIs
```
GET /api/v1/documents/{id}/download/
GET /api/v1/reports/{id}/download/
```
Both check permissions, verify the file exists on disk, and set proper
`Content-Disposition` / `Content-Type` headers.

### Module 12 — Dashboard
```
GET /api/v1/dashboard/                          # employee/department counts, salary & attendance stats
GET /api/v1/dashboard/export/?file_format=excel|pdf
```

## 4. Project / Folder Structure

```
company_portal/
├── company_portal/          # settings, root urls, wsgi/asgi
├── employees/
│   ├── models.py            # Employee, Department, Attendance
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   ├── excel_export.py      # export + Excel import (Module 3 & 4)
│   ├── pdf_generator.py     # profile / salary slip / ID card PDFs
│   ├── qr_generator.py
│   ├── csv_handler.py
│   └── management/commands/seed_roles.py
├── documents/
│   ├── models.py            # EmployeeDocument
│   ├── serializers.py / views.py / urls.py / permissions.py
├── reports/
│   ├── models.py             # ReportFile (supports re-download by id)
│   ├── excel_export.py / pdf_generator.py / csv_handler.py
│   ├── views.py / urls.py    # report generation + dashboard
├── media/
│   ├── employees/  documents/  reports/  id_cards/
├── requirements.txt
└── manage.py
```

## 5. Sample Employee Import Template Columns

```
Employee ID | First Name | Last Name | Email | Phone | Department | Designation | Salary | Joining Date
```
(Header row required exactly as above for both Excel and CSV import.)

## 6. Testing Notes

This project was verified end-to-end during development: migrations apply
cleanly, all PDF/Excel/CSV/QR generators produce valid output, and the
document permission matrix (HR full access / Manager read-only / Employee
own-records-only, no delete) was exercised via Django's test client.
