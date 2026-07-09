from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_file_size(value):
    """Reusable validator: rejects files bigger than 5MB."""
    if value.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f"File size must not exceed 5MB. Uploaded file is "
            f"{value.size / (1024 * 1024):.2f}MB."
        )


image_extension_validator = FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
pdf_extension_validator = FileExtensionValidator(allowed_extensions=['pdf'])


def employee_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"employees/{instance.employee_id}/profile_photo.{ext}"


def employee_resume_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"employees/{instance.employee_id}/resume.{ext}"


def employee_aadhaar_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"employees/{instance.employee_id}/aadhaar.{ext}"


def employee_pan_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"employees/{instance.employee_id}/pan.{ext}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Employee(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    # Optional link to an auth user, used for role-based / ownership permissions
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='employee_profile'
    )

    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees'
    )
    designation = models.CharField(max_length=100, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    joining_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    # ---- File uploads (Module 1) ----
    profile_photo = models.ImageField(
        upload_to=employee_photo_path, blank=True, null=True,
        validators=[image_extension_validator, validate_file_size],
        help_text="JPG or PNG, max 5MB.",
    )
    resume = models.FileField(
        upload_to=employee_resume_path, blank=True, null=True,
        validators=[pdf_extension_validator, validate_file_size],
        help_text="PDF only, max 5MB.",
    )
    aadhaar_document = models.FileField(
        upload_to=employee_aadhaar_path, blank=True, null=True,
        validators=[pdf_extension_validator, validate_file_size],
        help_text="PDF only, max 5MB.",
    )
    pan_document = models.FileField(
        upload_to=employee_pan_path, blank=True, null=True,
        validators=[pdf_extension_validator, validate_file_size],
        help_text="PDF only, max 5MB.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"
