from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from books.models import Book
from books.serializers import BookSerializer
from books.permissions import IsAdminUserOrReadOnly


@extend_schema_view(
    create=extend_schema(summary="Create book"),
    list=extend_schema(summary="List books"),
    retrieve=extend_schema(summary="Get book details"),
    update=extend_schema(summary="Update book"),
    partial_update=extend_schema(summary="Partially update book"),
    destroy=extend_schema(summary="Delete book"),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUserOrReadOnly]
