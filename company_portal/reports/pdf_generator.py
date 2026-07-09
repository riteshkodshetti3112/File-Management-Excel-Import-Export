"""
Module 10: Reports Module - PDF report builders.
"""
import io

from django.conf import settings
from django.db.models import Avg, Count
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from employees.models import Attendance, Department, Employee

styles = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=16)
HEADING_STYLE = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], textColor=colors.HexColor('#1f4e79'))


def _base_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


def _doc_with_title(title):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = [Paragraph(settings.COMPANY_NAME, TITLE_STYLE), Paragraph(title, HEADING_STYLE), Spacer(1, 10)]
    return buffer, doc, elements


def build_employee_report_pdf():
    buffer, doc, elements = _doc_with_title("Employee Report")

    elements.append(Paragraph("Active Employees", styles['Heading3']))
    data = [["Employee ID", "Name", "Department", "Designation"]]
    for emp in Employee.objects.filter(status='ACTIVE').select_related('department'):
        data.append([emp.employee_id, emp.full_name, emp.department.name if emp.department else '', emp.designation])
    elements.append(_base_table(data, [80, 150, 120, 120]))
    elements.append(Spacer(1, 16))

    elements.append(Paragraph("Inactive Employees", styles['Heading3']))
    data2 = [["Employee ID", "Name", "Department", "Designation"]]
    for emp in Employee.objects.filter(status='INACTIVE').select_related('department'):
        data2.append([emp.employee_id, emp.full_name, emp.department.name if emp.department else '', emp.designation])
    elements.append(_base_table(data2, [80, 150, 120, 120]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_department_report_pdf():
    buffer, doc, elements = _doc_with_title("Department Report")
    data = [["Department", "Employee Count", "Average Salary"]]
    for dept in Department.objects.annotate(employee_count=Count('employees'), avg_salary=Avg('employees__salary')):
        data.append([dept.name, dept.employee_count, f"₹ {float(dept.avg_salary or 0):,.2f}"])
    elements.append(_base_table(data, [200, 120, 150]))
    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_salary_report_pdf():
    buffer, doc, elements = _doc_with_title("Salary Report - Monthly Payroll")
    data = [["Employee ID", "Name", "Department", "Salary"]]
    total = 0
    for emp in Employee.objects.select_related('department').all():
        data.append([emp.employee_id, emp.full_name, emp.department.name if emp.department else '',
                     f"{float(emp.salary):,.2f}"])
        total += float(emp.salary)
    data.append(["", "", "Total Payroll", f"{total:,.2f}"])
    elements.append(_base_table(data, [80, 150, 120, 120]))
    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_attendance_report_pdf():
    buffer, doc, elements = _doc_with_title("Attendance Report")
    data = [["Employee ID", "Name", "Present", "Absent", "Leave"]]
    for emp in Employee.objects.all():
        present = Attendance.objects.filter(employee=emp, status='PRESENT').count()
        absent = Attendance.objects.filter(employee=emp, status='ABSENT').count()
        leave = Attendance.objects.filter(employee=emp, status='LEAVE').count()
        data.append([emp.employee_id, emp.full_name, present, absent, leave])
    elements.append(_base_table(data, [80, 150, 80, 80, 80]))
    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_dashboard_pdf(dashboard_data):
    buffer, doc, elements = _doc_with_title("Dashboard Summary")
    data = [
        ["Metric", "Value"],
        ["Total Employees", dashboard_data["employee_count"]],
        ["Active Employees", dashboard_data["active_employees"]],
        ["Inactive Employees", dashboard_data["inactive_employees"]],
        ["Total Departments", dashboard_data["department_count"]],
        ["Total Monthly Payroll", f"₹ {dashboard_data['salary_statistics']['total_payroll']:,.2f}"],
        ["Average Salary", f"₹ {dashboard_data['salary_statistics']['average_salary']:,.2f}"],
        ["Present Today", dashboard_data["attendance_summary"]["present"]],
        ["Absent Today", dashboard_data["attendance_summary"]["absent"]],
        ["On Leave Today", dashboard_data["attendance_summary"]["leave"]],
    ]
    elements.append(_base_table(data, [250, 150]))
    doc.build(elements)
    buffer.seek(0)
    return buffer
