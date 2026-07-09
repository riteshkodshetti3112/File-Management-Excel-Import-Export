import os

from django.http import FileResponse, Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employees.permissions import HR_GROUP, MANAGER_GROUP, _in_group
from .models import EmployeeDocument
from .permissions import CanManageDocuments
from .serializers import EmployeeDocumentSerializer


class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    """
    Module 2 Practical Task 2:
      - Upload Document   -> POST   /api/v1/documents/
      - List Documents     -> GET    /api/v1/documents/  (?employee=<id> to filter)
      - Retrieve Document  -> GET    /api/v1/documents/{id}/
      - Delete Document    -> DELETE /api/v1/documents/{id}/
      - Download Document  -> GET    /api/v1/documents/{id}/download/
    Role-based permissions enforced via CanManageDocuments.
    """
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated, CanManageDocuments]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = EmployeeDocument.objects.select_related('employee').all()
        user = self.request.user

        employee_filter = self.request.query_params.get('employee')
        if employee_filter:
            qs = qs.filter(employee_id=employee_filter)

        document_type = self.request.query_params.get('document_type')
        if document_type:
            qs = qs.filter(document_type=document_type)

        if user.is_superuser or _in_group(user, HR_GROUP, MANAGER_GROUP):
            return qs

        # Plain employees only see their own documents
        employee_profile = getattr(user, 'employee_profile', None)
        if employee_profile is None:
            return qs.none()
        return qs.filter(employee=employee_profile)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """GET /api/v1/documents/{id}/download/"""
        document = self.get_object()  # triggers has_object_permission check
        if not document.file or not os.path.exists(document.file.path):
            raise Http404("File not found on server.")
        return FileResponse(
            open(document.file.path, 'rb'),
            as_attachment=True,
            filename=os.path.basename(document.file.name),
        )
