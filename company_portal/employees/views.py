from datetime import date

from django.http import HttpResponse, FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import csv_handler, excel_export
from .models import Attendance, Department, Employee
from .pdf_generator import (
    generate_employee_profile_pdf, generate_id_card_pdf, generate_salary_slip_pdf,
)
from .permissions import IsHR, IsHRorManager, IsOwnerOrHRorManager
from .qr_generator import generate_and_save_employee_qr, get_qr_image_bytes
from .serializers import AttendanceSerializer, DepartmentSerializer, EmployeeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsHRorManager]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for Employee, including the file fields
    (profile_photo, resume, aadhaar_document, pan_document).
    """
    queryset = Employee.objects.select_related('department').all()
    serializer_class = EmployeeSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get_permissions(self):
        if self.action in ('retrieve',):
            return [IsAuthenticated(), IsOwnerOrHRorManager()]
        return super().get_permissions()


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated, IsHRorManager]


# ---------------------------------------------------------------------
# Module 3: Excel Import  -> POST /api/v1/employees/import/
# ---------------------------------------------------------------------
class EmployeeExcelImportView(APIView):
    permission_classes = [IsAuthenticated, IsHR]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"detail": "No file uploaded. Use form field 'file'."},
                             status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith(('.xlsx', '.xlsm')):
            return Response({"detail": "Only .xlsx files are supported."},
                             status=status.HTTP_400_BAD_REQUEST)

        summary = excel_export.import_employees_excel(uploaded_file)
        return Response(summary, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# Module 4: Excel Export -> GET /api/v1/employees/export/?type=employees
# ---------------------------------------------------------------------
class EmployeeExcelExportView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get(self, request):
        export_type = request.query_params.get('type', 'employees')

        if export_type == 'employees':
            buffer = excel_export.export_employee_list(Employee.objects.select_related('department').all())
            filename = 'Employee_List.xlsx'
        elif export_type == 'departments':
            buffer = excel_export.export_department_list(Department.objects.all())
            filename = 'Department_List.xlsx'
        elif export_type == 'salary':
            buffer = excel_export.export_salary_report(Employee.objects.select_related('department').all())
            filename = 'Salary_Report.xlsx'
        elif export_type == 'attendance':
            buffer = excel_export.export_attendance_report(Attendance.objects.select_related('employee').all())
            filename = 'Attendance_Report.xlsx'
        else:
            return Response({"detail": "Invalid 'type'. Use employees|departments|salary|attendance."},
                             status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ---------------------------------------------------------------------
# Module 5: CSV Import / Export
# ---------------------------------------------------------------------
class EmployeeCSVImportView(APIView):
    permission_classes = [IsAuthenticated, IsHR]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"detail": "No file uploaded. Use form field 'file'."},
                             status=status.HTTP_400_BAD_REQUEST)
        if not uploaded_file.name.lower().endswith('.csv'):
            return Response({"detail": "Only .csv files are supported."},
                             status=status.HTTP_400_BAD_REQUEST)

        summary = csv_handler.import_employees_csv(uploaded_file)
        return Response(summary, status=status.HTTP_200_OK)


class EmployeeCSVExportView(APIView):
    permission_classes = [IsAuthenticated, IsHRorManager]

    def get(self, request):
        csv_text = csv_handler.export_employees_csv(Employee.objects.select_related('department').all())
        response = HttpResponse(csv_text, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="Employee_List.csv"'
        return response


# ---------------------------------------------------------------------
# Module 6: Employee Profile PDF -> GET /api/v1/employees/{id}/profile-pdf/
# ---------------------------------------------------------------------
class EmployeeProfilePDFView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrHRorManager]

    def get(self, request, pk):
        employee = Employee.objects.select_related('department').get(pk=pk)
        self.check_object_permissions(request, employee)
        buffer = generate_employee_profile_pdf(employee)
        filename = f"{employee.employee_id}_Profile.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type='application/pdf')


# ---------------------------------------------------------------------
# Module 7: Salary Slip PDF -> GET /api/v1/employees/{id}/salary-slip/?month=June&year=2026
# ---------------------------------------------------------------------
class SalarySlipPDFView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrHRorManager]

    def get(self, request, pk):
        employee = Employee.objects.select_related('department').get(pk=pk)
        self.check_object_permissions(request, employee)

        month = request.query_params.get('month', date.today().strftime('%B'))
        year = request.query_params.get('year', str(date.today().year))
        month_label = f"{month} {year}"

        allowances = {
            "House Rent Allowance": float(employee.salary) * 0.20,
            "Conveyance Allowance": 1600.0,
            "Medical Allowance": 1250.0,
        }
        deductions = {
            "Provident Fund": float(employee.salary) * 0.12,
            "Professional Tax": 200.0,
        }

        buffer = generate_salary_slip_pdf(employee, month_label, employee.salary, allowances, deductions)
        filename = f"SalarySlip_{month}_{year}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type='application/pdf')


# ---------------------------------------------------------------------
# Module 9: Employee ID Card -> GET /api/v1/employees/{id}/id-card/
# ---------------------------------------------------------------------
class EmployeeIDCardPDFView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrHRorManager]

    def get(self, request, pk):
        employee = Employee.objects.select_related('department').get(pk=pk)
        self.check_object_permissions(request, employee)

        valid_until_str = request.query_params.get('valid_until')
        if valid_until_str:
            valid_until = date.fromisoformat(valid_until_str)
        else:
            valid_until = date(date.today().year + 1, date.today().month, date.today().day)

        buffer = generate_id_card_pdf(employee, valid_until)
        filename = f"ID_{employee.employee_id}.pdf"
        return FileResponse(buffer, as_attachment=True, filename=filename, content_type='application/pdf')


# ---------------------------------------------------------------------
# Module 8: QR Code -> GET /api/v1/employees/{id}/qr-code/
# ---------------------------------------------------------------------
class EmployeeQRCodeView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrHRorManager]

    def get(self, request, pk):
        employee = Employee.objects.select_related('department').get(pk=pk)
        self.check_object_permissions(request, employee)

        if request.query_params.get('save') == 'true':
            relative_path = generate_and_save_employee_qr(employee)
            return Response({"saved_path": relative_path})

        image_bytes = get_qr_image_bytes(employee)
        return HttpResponse(image_bytes, content_type='image/png')
