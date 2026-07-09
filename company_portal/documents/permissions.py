from rest_framework.permissions import BasePermission

from employees.permissions import HR_GROUP, MANAGER_GROUP, _in_group


class CanManageDocuments(BasePermission):
    """
    HR: full access (upload/download/delete/list, any employee).
    Manager: list/download for employees in their scope (simplified: all).
    Employee: may only list/download/upload their OWN documents; cannot delete.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or _in_group(user, HR_GROUP):
            return True

        employee_profile = getattr(user, 'employee_profile', None)
        is_owner = employee_profile is not None and obj.employee_id == employee_profile.id

        if _in_group(user, MANAGER_GROUP):
            # Managers can view/download but not delete other employees' documents
            if view.action == 'destroy':
                return is_owner
            return True

        # Plain "Employee" role: only their own documents, and cannot delete
        if view.action == 'destroy':
            return False
        return is_owner
