from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Decorator to check if user has required role(s).
    Usage: @role_required('Admin', 'Manager')
    DEPRECATED: Use module_required for database-driven permissions
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login first")
                return redirect('login')
            
            if request.user.role not in roles:
                messages.error(request, "You don't have permission to access this page")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def module_required(module_name):
    """
    Decorator to check module access from database.
    Usage: @module_required('production')
    
    module_name should match the 'module' field in RolePermission model
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login first")
                return redirect('login')
            
            # Import here to avoid circular imports
            from .models import RolePermission
            
            if not RolePermission.has_module_access(request.user.role, module_name):
                messages.error(request, "You don't have permission to access this page")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_only(view_func):
    """Decorator to restrict access to Admin only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect('login')
        
        if request.user.role != 'Admin':
            messages.error(request, "Only admins can access this page")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_manager_only(view_func):
    """Decorator to restrict access to Admin and Manager only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please login first")
            return redirect('login')
        
        if request.user.role not in ['Admin', 'Manager']:
            messages.error(request, "You don't have permission to access this page")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def check_permission(role, module):
    """
    Utility function to check if a role has access to a module.
    Can be used in templates via template tags or in Python code.
    
    Usage in Python:
        from .decorators import check_permission
        if check_permission('Manager', 'production'):
            # show something
    """
    from .models import RolePermission
    return RolePermission.has_module_access(role, module)
