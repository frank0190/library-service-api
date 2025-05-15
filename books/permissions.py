from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadOnly(BasePermission):
    """
    Grants full access to administrators,
    while read-only access (GET, HEAD, OPTIONS) is permitted
    for all users, including unauthenticated users.
    """

    def has_permission(self, request, view) -> bool:
        if hasattr(view, "action") and view.action == "list":
            return True
        return request.user and request.user.is_staff
