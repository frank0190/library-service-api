from __future__ import annotations
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def detail_url(book_id: int) -> Response:
    return reverse("books:book-detail", args=[book_id])


def create_book(as_dict: bool = False, **params) -> Book | bool:
    defaults = {
        "name": "test_name",
        "author": "test_author",
        "cover": "SOFT",
        "inventory": 10,
        "daily_fee": 10.00,
    }
    defaults.update(params)
    return defaults if as_dict else Book.objects.create(**defaults)


class UnauthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.book_1 = create_book(name="test_2")
        self.book_2 = create_book(name="test_1")

    def test_available_endpoints(self) -> None:
        list_response = self.client.get(BOOK_URL)
        detail_response = self.client.get(detail_url(self.book_1.id))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_unavailable_endpoints(self) -> None:
        create_response = self.client.post(BOOK_URL, {})
        update_response = self.client.put(detail_url(self.book_1.id), {})
        delete_response = self.client.delete(detail_url(self.book_1.id))

        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedUserTest(UnauthenticatedUserTest):
    def setUp(self) -> None:
        super().setUp()

        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="test123user"
        )
        self.client.force_authenticate(self.user)


class AdminUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@admin.com", password="test123user", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.book_1 = create_book(name="test_1")
        self.book_2 = create_book(name="test_2")

    def test_book_list(self) -> None:
        response = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_book_detail(self) -> None:
        response = self.client.get(detail_url(self.book_1.id))
        serializer = BookSerializer(self.book_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_book_create(self) -> None:
        payload = create_book(as_dict=True)
        response = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for field in payload:
            self.assertEqual(getattr(book, field), payload[field])
