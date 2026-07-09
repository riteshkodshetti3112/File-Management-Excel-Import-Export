# HRMS Document & Reporting Module

A Django REST Framework based HRMS Document & Reporting System that provides employee document management, Excel/CSV import & export, PDF generation, QR code generation, ID card generation, dashboard reports, and file download APIs.

---

# Features

## Employee File Uploads

- Profile Photo Upload
- Resume Upload
- Aadhaar Document Upload
- PAN Document Upload
- File Validation
- Image Validation (JPG, PNG)
- PDF Validation
- Maximum File Size (5 MB)

---

# Document Management

Employee Document Module

Supported Documents

- Resume
- Aadhaar
- PAN
- Degree Certificate
- Experience Certificate
- Offer Letter

APIs

- Upload Document
- Download Document
- Delete Document
- List Documents

Role-Based Permissions

- Admin
- HR
- Manager
- Employee

---

# Excel Import

Import Employees using Excel (.xlsx)

Columns

- Employee ID
- First Name
- Last Name
- Email
- Phone
- Department
- Designation
- Salary
- Joining Date

Features

- Row Validation
- Skip Invalid Records
- Bulk Import
- Import Summary

Example Response

```json
{
    "total_rows": 500,
    "created": 485,
    "failed": 15,
    "errors": []
}
```

---

# Excel Export

Export

- Employee List
- Department List
- Salary Report
- Attendance Report

Output Format

- XLSX

---

# CSV Import & Export

Features

- UTF-8 Encoding
- Header Validation
- Duplicate Detection
- CSV Upload
- CSV Download

---

# PDF Generation

Generate Employee Profile PDF

Contains

- Employee Information
- Department
- Salary
- Joining Date
- Contact Details

Output

```
EMP001_Profile.pdf
```

---

# Salary Slip Generation

Professional Salary Slip

Contains

- Company Name
- Employee Details
- Basic Salary
- Allowances
- Deductions
- Net Salary

Output

```
SalarySlip_June_2026.pdf
```

---

# QR Code Generation

Generate QR Code containing

- Employee ID
- Employee Name
- Department
- Verification URL

Used In

- Employee ID Card
- Employee Profile
- PDF Reports

---

# Employee ID Card

Contains

- Company Logo
- Employee Photo
- Employee ID
- Employee Name
- Department
- QR Code
- Validity Date

Output

```
ID_EMP001.pdf
```

---

# Reports

Generate Reports

Employee Report

- Active Employees
- Inactive Employees

Department Report

- Employee Count
- Average Salary

Salary Report

- Monthly Payroll
- Department Salary Summary

Attendance Report

- Present
- Absent
- Leave

Export Formats

- PDF
- Excel
- CSV

---

# Dashboard Reports

Dashboard APIs

Return

- Employee Count
- Department Count
- Salary Statistics
- Attendance Summary

Dashboard Export

- Excel
- PDF

---

# File Download APIs

- Download Employee Documents
- Download Reports

Validation

- Permission Check
- File Exists Validation
- Proper Response Headers

---

# Project Structure

```
company_portal/

│
├── employees/
│
├── documents/
│
├── reports/
│   ├── excel_export.py
│   ├── pdf_generator.py
│   ├── qr_generator.py
│   ├── csv_handler.py
│   ├── views.py
│   └── serializers.py
│
├── media/
│   ├── employees/
│   ├── documents/
│   ├── reports/
│   └── id_cards/
│
├── manage.py
└── requirements.txt
```

---

# Installation

Clone Repository

```bash
git clone <repository_url>
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

Start Development Server

```bash
python manage.py runserver
```

---

# Required Packages

```bash
pip install django
pip install djangorestframework
pip install pillow
pip install openpyxl
pip install reportlab
pip install qrcode
```

---

# Git Workflow

```bash
git checkout development

git pull origin development

git checkout -b feature/file-management-reporting
```

After Development

```bash
git add .

git commit -m "Implemented HRMS Document & Reporting Module"

git push -u origin feature/file-management-reporting
```

---

# Technologies Used

- Python
- Django
- Django REST Framework
- SQLite / PostgreSQL
- OpenPyXL
- ReportLab
- QRCode
- Pillow

---

# Author

Ritesh Kodshetti

Python Developer
