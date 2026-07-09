import os
from datetime import date

from django.core.files.base import ContentFile
from django.db.models import Avg, Sum
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import EmployeeDocument
from employees.models import Attendance, Department, Employee
from employees.permissions import IsHRorManager

from . import csv_handler, excel_export, pdf_generator
from .models import ReportFile

CONTENT_TYPES = {
    'PDF': 'application/pdf',
    'EXCEL': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'CSV': 'text/csv; charset=utf-8',
}
EXTENSIONS = {'PDF': 'pdf', 'EXCEL': 'xlsx', 'CSV': 'csv'}

BUILDERS = {
    ('EMPLOYEE', 'PDF'): pdf_generator.build_employee_report_pdf,
    ('EMPLOYEE', 'EXCEL'): excel_export.build_employee_report_excel,
    ('EMPLOYEE', 'CSV'): csv_handler.build_employee_report_csv,
    ('DEPARTMENT', 'PDF'): pdf_generator.build_department_report_pdf,
    ('DEPARTMENT', 'EXCEL'): excel_export.build_department_report_excel,
    ('DEPARTMENT', 'CSV'): csv_handler.build_department_report_csv,
    ('SALARY', 'PDF'): pdf_generator.build_salary_report_pdf,
    ('SALARY', 'EXCEL'): excel_export.build_salary_report_excel,
    ('SALARY', 'CSV'): csv_handler.build_salary_report_csv,
    ('ATTENDANCE', 'PDF'): pdf_generator.build_attendance_report_pdf,
    ('ATTENDANCE', 'EXCEL'): excel_export.build_attendance_report_excel,
    ('ATTENDANCE', 'CSV'): csv_handler.build_attendance_report_csv,
}


def _normalize_format(request):
    fmt = request.query_params.get('file_format', 'pdf').upper()
    if fmt not in ('PDF', 'EXCEL', 'CSV'):
        fmt = 'PDF'
    return fmt


def _persist_and_respond(report_type, file_format, content, user, filename):
    """Saves a ReportFile record (Module 11 re-download support) and streams the response."""
    report = ReportFile(report_type=report_type, file_format=file_format, generated_by=user if user.is_authenticated else None)

    if isinstance(content, str):
        data_bytes = content.encode('utf-8')
    else:
        data_bytes = content.getvalue() if hasattr(content, 'getvalue') else content

    report.file.save(filename, ContentFile(data_bytes), save=True)

    response = HttpResponse(data_bytes, content_type=CONTENT_TYPES[file_format])
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['X-Report-Id'] = str(report.id)
    return response


class BaseReportView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]
    report_type = None  # override in subclass

    def get(self, request):
        fmt = _normalize_format(request)
        builder = BUILDERS.get((self.report_type, fmt))
        if builder is None:
            return Response({"detail": "Unsupported report/format combination."},
                             status=status.HTTP_400_BAD_REQUEST)
        content = builder()
        filename = f"{self.report_type}_Report_{date.today().isoformat()}.{EXTENSIONS[fmt]}"
        return _persist_and_respond(self.report_type, fmt, content, request.user, filename)


class EmployeeReportView(BaseReportView):
    report_type = 'EMPLOYEE'


class DepartmentReportView(BaseReportView):
    report_type = 'DEPARTMENT'


class SalaryReportView(BaseReportView):
    report_type = 'SALARY'


class AttendanceReportView(BaseReportView):
    report_type = 'ATTENDANCE'


# ---------------------------------------------------------------------
# Module 11: File Download APIs -> GET /api/v1/reports/{id}/download/
# ---------------------------------------------------------------------
class ReportDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get(self, request, pk):
        try:
            report = ReportFile.objects.get(pk=pk)
        except ReportFile.DoesNotExist:
            raise Http404("Report not found.")

        if not report.file or not os.path.exists(report.file.path):
            raise Http404("Report file no longer exists on the server.")

        content_type = CONTENT_TYPES.get(report.file_format, 'application/octet-stream')
        response = FileResponse(
            open(report.file.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(report.file.name),
            content_type=content_type,
        )
        return response


# ---------------------------------------------------------------------
# Module 12: Dashboard Reports
# ---------------------------------------------------------------------
def _build_dashboard_data():
    total_payroll = Employee.objects.aggregate(total=Sum('salary'))['total'] or 0
    average_salary = Employee.objects.aggregate(avg=Avg('salary'))['avg'] or 0
    today = date.today()

    return {
        "employee_count": Employee.objects.count(),
        "active_employees": Employee.objects.filter(status='ACTIVE').count(),
        "inactive_employees": Employee.objects.filter(status='INACTIVE').count(),
        "department_count": Department.objects.count(),
        "document_count": EmployeeDocument.objects.count(),
        "salary_statistics": {
            "total_payroll": float(total_payroll),
            "average_salary": round(float(average_salary), 2),
        },
        "attendance_summary": {
            "present": Attendance.objects.filter(date=today, status='PRESENT').count(),
            "absent": Attendance.objects.filter(date=today, status='ABSENT').count(),
            "leave": Attendance.objects.filter(date=today, status='LEAVE').count(),
        },
    }


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get(self, request):
        return Response(_build_dashboard_data())


class DashboardExportView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get(self, request):
        fmt = request.query_params.get('file_format', 'excel').upper()
        dashboard_data = _build_dashboard_data()

        if fmt == 'PDF':
            content = pdf_generator.build_dashboard_pdf(dashboard_data)
            file_format = 'PDF'
        else:
            content = excel_export.build_dashboard_excel(dashboard_data)
            file_format = 'EXCEL'

        filename = f"Dashboard_{date.today().isoformat()}.{EXTENSIONS[file_format]}"
        return _persist_and_respond('DASHBOARD', file_format, content, request.user, filename)
