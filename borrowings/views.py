from django.utils.timezone import now
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter
)
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.notifications.telegram import send_telegram_message
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer
)


@extend_schema_view(
    create=extend_schema(summary="Create borrowing"),
    retrieve=extend_schema(summary="Get borrowing details"),
)
class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.select_related()
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
            return (
                BorrowingAdminListSerializer
                if self.request.user.is_staff
                else BorrowingListSerializer
            )
        if self.action == "retrieve":
            return (
                BorrowingAdminDetailSerializer
                if self.request.user.is_staff
                else BorrowingDetailSerializer
            )
        return BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        borrowing = serializer.save(user=self.request.user)

        message = (
            f"Created new borrowing!\n"
            f"\n"
            f"User: {borrowing.user.get_full_name()}\n"
            f"Book: {borrowing.book.__str__()}\n"
            f"Data of borrowing: {borrowing.borrow_date}\n"
            f"Expected return date: {borrowing.expected_return_date}\n"
        )
        send_telegram_message(message)

    @extend_schema(
        summary="List borrowings",
        description="Returns a list of borrowings with optional params.",
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.STR,
                description="Filter by is_active field, choose from true/false options.",
                required=False
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                description="Filter by user_id field.",
                required=False
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={status.HTTP_200_OK: {"detail": "The book returned successfully."}}
    )
    @action(methods=["GET"], detail=True, url_path="return")
    def return_book(self, request, pk=None):
        """Return the book in library and close the borrowing."""
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
