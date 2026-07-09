"""
Module 6: PDF Generation
Module 7: Salary Slip Generation
Module 9: Employee ID Card Generator

All functions return an io.BytesIO buffer containing the generated PDF,
ready to be wrapped in an HttpResponse / FileResponse by the view.
"""
import io

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from .qr_generator import get_qr_image_bytes

styles = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=6)
HEADING_STYLE = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], textColor=colors.HexColor('#1f4e79'))
NORMAL_STYLE = styles['Normal']


def _company_header(elements):
    elements.append(Paragraph(settings.COMPANY_NAME, TITLE_STYLE))
    elements.append(Paragraph(settings.COMPANY_ADDRESS, NORMAL_STYLE))
    elements.append(Spacer(1, 12))


# ---------------------------------------------------------------------
# Employee Profile PDF  (EMP001_Profile.pdf)
# ---------------------------------------------------------------------
def generate_employee_profile_pdf(employee):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []

    _company_header(elements)
    elements.append(Paragraph("Employee Profile", HEADING_STYLE))
    elements.append(Spacer(1, 10))

    department_name = employee.department.name if employee.department else 'N/A'
    data = [
        ["Employee ID", employee.employee_id],
        ["Name", employee.full_name],
        ["Department", department_name],
        ["Designation", employee.designation or 'N/A'],
        ["Salary", f"₹ {employee.salary:,.2f}"],
        ["Joining Date", employee.joining_date.strftime('%d-%b-%Y') if employee.joining_date else 'N/A'],
        ["Email", employee.email],
        ["Phone", employee.phone or 'N/A'],
        ["Status", employee.status],
    ]
    table = Table(data, colWidths=[150, 320])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbe5f1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------
# Salary Slip PDF (SalarySlip_June_2026.pdf)
# ---------------------------------------------------------------------
def generate_salary_slip_pdf(employee, month_label, basic_salary, allowances, deductions):
    """
    allowances / deductions: dict of {label: amount}
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []

    _company_header(elements)
    elements.append(Paragraph(f"Salary Slip - {month_label}", HEADING_STYLE))
    elements.append(Spacer(1, 10))

    department_name = employee.department.name if employee.department else 'N/A'
    emp_info = [
        ["Employee ID", employee.employee_id, "Department", department_name],
        ["Name", employee.full_name, "Designation", employee.designation or 'N/A'],
    ]
    emp_table = Table(emp_info, colWidths=[90, 150, 90, 130])
    emp_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbe5f1')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#dbe5f1')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 14))

    total_allowances = sum(allowances.values())
    total_deductions = sum(deductions.values())
    net_salary = float(basic_salary) + total_allowances - total_deductions

    earnings_rows = [["Earnings", "Amount (₹)"], ["Basic Salary", f"{float(basic_salary):,.2f}"]]
    for label, amount in allowances.items():
        earnings_rows.append([label, f"{amount:,.2f}"])
    earnings_rows.append(["Total Earnings", f"{float(basic_salary) + total_allowances:,.2f}"])

    deductions_rows = [["Deductions", "Amount (₹)"]]
    for label, amount in deductions.items():
        deductions_rows.append([label, f"{amount:,.2f}"])
    deductions_rows.append(["Total Deductions", f"{total_deductions:,.2f}"])

    earnings_table = Table(earnings_rows, colWidths=[130, 100])
    deductions_table = Table(deductions_rows, colWidths=[130, 100])
    for t in (earnings_table, deductions_table):
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))

    side_by_side = Table([[earnings_table, deductions_table]], colWidths=[240, 240])
    side_by_side.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    elements.append(side_by_side)
    elements.append(Spacer(1, 16))

    net_table = Table([["Net Salary", f"₹ {net_salary:,.2f}"]], colWidths=[130, 110])
    net_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#c6efce')),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(net_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------------------
# Employee ID Card PDF (ID_EMP001.pdf)
# ---------------------------------------------------------------------
def generate_id_card_pdf(employee, valid_until, logo_path=None):
    """
    Generates a landscape, credit-card-styled ID card PDF containing photo,
    QR code, employee ID, name, department and validity date.
    """
    card_width, card_height = 100 * mm, 65 * mm
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(card_width, card_height))

    # Background
    c.setFillColor(colors.HexColor('#1f4e79'))
    c.rect(0, card_height - 16 * mm, card_width, 16 * mm, fill=1, stroke=0)

    # Logo (optional)
    if logo_path:
        try:
            c.drawImage(logo_path, 4 * mm, card_height - 14 * mm, width=12 * mm, height=12 * mm,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(18 * mm, card_height - 10 * mm, settings.COMPANY_NAME[:28])

    # Photo
    photo_box_x, photo_box_y = 5 * mm, 5 * mm
    photo_w, photo_h = 24 * mm, 30 * mm
    c.setFillColor(colors.HexColor('#f2f2f2'))
    c.rect(photo_box_x, photo_box_y, photo_w, photo_h, fill=1, stroke=1)
    if employee.profile_photo and hasattr(employee.profile_photo, 'path'):
        try:
            c.drawImage(employee.profile_photo.path, photo_box_x, photo_box_y,
                        width=photo_w, height=photo_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # Employee details
    text_x = 32 * mm
    text_y = card_height - 22 * mm
    department_name = employee.department.name if employee.department else 'N/A'

    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(text_x, text_y, employee.full_name)
    c.setFont('Helvetica', 8)
    c.drawString(text_x, text_y - 5 * mm, f"ID: {employee.employee_id}")
    c.drawString(text_x, text_y - 10 * mm, f"Dept: {department_name}")
    c.drawString(text_x, text_y - 15 * mm, f"Designation: {employee.designation or 'N/A'}")
    c.drawString(text_x, text_y - 20 * mm, f"Valid Until: {valid_until.strftime('%d-%b-%Y')}")

    # QR code
    qr_bytes = get_qr_image_bytes(employee)
    qr_image = ImageReader(io.BytesIO(qr_bytes))
    qr_size = 20 * mm
    c.drawImage(qr_image, card_width - qr_size - 4 * mm, 5 * mm, width=qr_size, height=qr_size,
                preserveAspectRatio=True, mask='auto')

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
