from rest_framework.permissions import BasePermission, SAFE_METHODS

HR_GROUP = 'HR'
MANAGER_GROUP = 'Manager'
EMPLOYEE_GROUP = 'Employee'


def _in_group(user, *group_names):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__in=group_names).exists()
    )


class IsHR(BasePermission):
    """Only HR (or superuser) may perform the action."""

    def has_permission(self, request, view):
        return _in_group(request.user, HR_GROUP)


class IsHRorManager(BasePermission):
    """HR or Manager (or superuser) may perform the action."""

    def has_permission(self, request, view):
        return _in_group(request.user, HR_GROUP, MANAGER_GROUP)


class IsHROrReadOnlyManager(BasePermission):
    """HR has full access; Manager has read-only access; others denied."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if _in_group(request.user, HR_GROUP) or request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS and _in_group(request.user, MANAGER_GROUP):
            return True
        return False


class IsOwnerOrHRorManager(BasePermission):
    """
    Object-level permission: HR/Manager can access any employee's record.
    A plain Employee-group user may only access their own record/documents.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser or _in_group(user, HR_GROUP, MANAGER_GROUP):
            return True

        employee_profile = getattr(user, 'employee_profile', None)
        if employee_profile is None:
            return False

        # obj can be an Employee instance or anything with an `employee` FK
        target_employee = obj if hasattr(obj, 'employee_id') and not hasattr(obj, 'employee') else getattr(obj, 'employee', obj)
        return target_employee.pk == employee_profile.pk
