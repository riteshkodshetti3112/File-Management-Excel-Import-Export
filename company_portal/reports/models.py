from django.conf import settings
from django.db import models


def report_file_path(instance, filename):
    return f"reports/{instance.report_type}/{filename}"


class ReportFile(models.Model):
    """
    Persisted copy of a generated report so it can be re-downloaded later via
    GET /api/v1/reports/{id}/download/ (Module 11).
    """
    REPORT_TYPE_CHOICES = (
        ('EMPLOYEE', 'Employee Report'),
        ('DEPARTMENT', 'Department Report'),
        ('SALARY', 'Salary Report'),
        ('ATTENDANCE', 'Attendance Report'),
        ('DASHBOARD', 'Dashboard Export'),
    )
    FORMAT_CHOICES = (
        ('PDF', 'PDF'),
        ('EXCEL', 'Excel'),
        ('CSV', 'CSV'),
    )

    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to=report_file_path)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.report_type} ({self.file_format}) - {self.generated_at:%Y-%m-%d %H:%M}"
