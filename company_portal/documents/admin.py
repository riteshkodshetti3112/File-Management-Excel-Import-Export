from django.contrib import admin

from .models import EmployeeDocument


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'document_name', 'uploaded_at')
    list_filter = ('document_type',)
    search_fields = ('document_name', 'employee__employee_id', 'employee__first_name')
