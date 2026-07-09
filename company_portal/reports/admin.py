from django.contrib import admin

from .models import ReportFile


@admin.register(ReportFile)
class ReportFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'file_format', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'file_format')
