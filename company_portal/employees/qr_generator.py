import io
import os

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile


def build_qr_payload(employee):
    """Human readable payload embedded inside the QR code."""
    verification_url = f"{settings.VERIFICATION_BASE_URL.rstrip('/')}/{employee.employee_id}/"
    department_name = employee.department.name if employee.department else 'N/A'
    lines = [
        f"Employee ID: {employee.employee_id}",
        f"Name: {employee.full_name}",
        f"Department: {department_name}",
        f"Verify: {verification_url}",
    ]
    return "\n".join(lines), verification_url


def generate_employee_qr_image(employee):
    
    payload, verification_url = build_qr_payload(employee)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img, payload, verification_url


def generate_and_save_employee_qr(employee):
    
    img, _payload, _url = generate_employee_qr_image(employee)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    relative_dir = f"employees/{employee.employee_id}"
    absolute_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
    os.makedirs(absolute_dir, exist_ok=True)

    relative_path = f"{relative_dir}/qr_code.png"
    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    with open(absolute_path, 'wb') as fh:
        fh.write(buffer.getvalue())

    return relative_path


def get_qr_image_bytes(employee):
    
    img, _payload, _url = generate_employee_qr_image(employee)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()
