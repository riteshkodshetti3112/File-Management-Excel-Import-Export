from django.urls import path

from . import views

urlpatterns = [
    path('reports/employee/', views.EmployeeReportView.as_view(), name='report-employee'),
    path('reports/department/', views.DepartmentReportView.as_view(), name='report-department'),
    path('reports/salary/', views.SalaryReportView.as_view(), name='report-salary'),
    path('reports/attendance/', views.AttendanceReportView.as_view(), name='report-attendance'),
    path('reports/<int:pk>/download/', views.ReportDownloadView.as_view(), name='report-download'),

    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/export/', views.DashboardExportView.as_view(), name='dashboard-export'),
]
