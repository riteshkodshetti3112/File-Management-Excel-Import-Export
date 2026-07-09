from rest_framework import serializers

from .models import ReportFile


class ReportFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFile
        fields = ['id', 'report_type', 'file_format', 'file', 'generated_by', 'generated_at']
        read_only_fields = fields
