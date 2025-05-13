from django.utils.timezone import now
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        if self.request.user.is_staff:

            is_active = self.request.query_params.get("is_active")
            if is_active:
                queryset = queryset.filter(is_active=is_active == "true")

            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            return queryset
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingAdminListSerializer if self.request.user.is_staff else BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingAdminDetailSerializer if self.request.user.is_staff else BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)


    @action(methods=["GET"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.is_active:
            borrowing.is_active = False
            borrowing.actual_return_date = now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()
            return Response(
                {"detail": "The book returned successfully."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "This book is already returned."},
            status=status.HTTP_400_BAD_REQUEST
        )
