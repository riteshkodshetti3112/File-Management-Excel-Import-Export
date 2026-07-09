from django.core.validators import FileExtensionValidator
from django.db import models

from employees.models import Employee, validate_file_size


def employee_document_path(instance, filename):
    return f"documents/{instance.employee.employee_id}/{instance.document_type}_{filename}"


class EmployeeDocument(models.Model):
    """
    Module 2: Document Management

    Supported document types: Resume, Aadhaar, PAN, Degree Certificate,
    Experience Certificate, Offer Letter.
    """
    DOCUMENT_TYPE_CHOICES = (
        ('RESUME', 'Resume'),
        ('AADHAAR', 'Aadhaar'),
        ('PAN', 'PAN'),
        ('DEGREE_CERTIFICATE', 'Degree Certificate'),
        ('EXPERIENCE_CERTIFICATE', 'Experience Certificate'),
        ('OFFER_LETTER', 'Offer Letter'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(
        upload_to=employee_document_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_size,
        ],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.document_type} - {self.document_name}"
