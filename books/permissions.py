from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadOnly(BasePermission):
    """
    Grants full access to administrators,
    while read-only access (GET, HEAD, OPTIONS) is permitted
    for all users, including unauthenticated users.
    """

    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS or (
            request.user and request.user.is_staff
        )
