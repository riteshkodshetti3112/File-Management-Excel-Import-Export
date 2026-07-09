"""
Module 10: Reports Module - CSV report builders (UTF-8 encoded).
"""
import csv
import io

from employees.models import Attendance, Department, Employee


def _write_csv(rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for row in rows:
        writer.writerow(row)
    return '\ufeff' + buffer.getvalue()


def build_employee_report_csv():
    rows = [["Employee ID", "Name", "Department", "Designation", "Status", "Joining Date"]]
    for emp in Employee.objects.select_related('department').all():
        rows.append([
            emp.employee_id, emp.full_name, emp.department.name if emp.department else '',
            emp.designation, emp.status,
            emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else '',
        ])
    return _write_csv(rows)


def build_department_report_csv():
    from django.db.models import Avg, Count
    rows = [["Department", "Employee Count", "Average Salary"]]
    for dept in Department.objects.annotate(employee_count=Count('employees'), avg_salary=Avg('employees__salary')):
        rows.append([dept.name, dept.employee_count, round(float(dept.avg_salary or 0), 2)])
    return _write_csv(rows)


def build_salary_report_csv():
    rows = [["Employee ID", "Name", "Department", "Salary"]]
    for emp in Employee.objects.select_related('department').all():
        rows.append([emp.employee_id, emp.full_name,
                     emp.department.name if emp.department else '', float(emp.salary)])
    return _write_csv(rows)


def build_attendance_report_csv():
    rows = [["Employee ID", "Name", "Present", "Absent", "Leave"]]
    for emp in Employee.objects.all():
        present = Attendance.objects.filter(employee=emp, status='PRESENT').count()
        absent = Attendance.objects.filter(employee=emp, status='ABSENT').count()
        leave = Attendance.objects.filter(employee=emp, status='LEAVE').count()
        rows.append([emp.employee_id, emp.full_name, present, absent, leave])
    return _write_csv(rows)
