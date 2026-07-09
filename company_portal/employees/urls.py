from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'departments', views.DepartmentViewSet, basename='department')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('employees/import/', views.EmployeeExcelImportView.as_view(), name='employee-import-excel'),
    path('employees/export/', views.EmployeeExcelExportView.as_view(), name='employee-export-excel'),
    path('employees/import-csv/', views.EmployeeCSVImportView.as_view(), name='employee-import-csv'),
    path('employees/export-csv/', views.EmployeeCSVExportView.as_view(), name='employee-export-csv'),

    path('employees/<int:pk>/profile-pdf/', views.EmployeeProfilePDFView.as_view(), name='employee-profile-pdf'),
    path('employees/<int:pk>/salary-slip/', views.SalarySlipPDFView.as_view(), name='employee-salary-slip'),
    path('employees/<int:pk>/id-card/', views.EmployeeIDCardPDFView.as_view(), name='employee-id-card'),
    path('employees/<int:pk>/qr-code/', views.EmployeeQRCodeView.as_view(), name='employee-qr-code'),

    path('', include(router.urls)),
]
