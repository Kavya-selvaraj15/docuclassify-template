from functools import wraps
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    View decorator for RBAC access control.

    Usage:
        @role_required("admin", "auditor")
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                raise PermissionDenied("You don't have permission to access this resource.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
