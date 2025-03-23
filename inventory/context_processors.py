def user_roles(request):
    """Add user role information to the template context"""
    if request.user.is_authenticated:
        is_user_role = (
            request.user.groups.filter(name="User").exists()
            or request.user.is_superuser
        )
        return {"is_user_role": is_user_role}
    return {"is_user_role": False}
