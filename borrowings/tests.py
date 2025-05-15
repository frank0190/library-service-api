from datetime import date
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from borrowings.models import Borrowing
from books.tests import create_book
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminDetailSerializer
)


BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id: int) -> Response:
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def create_borrowing(as_dict: bool=False, **params):
    defaults = {
        "expected_return_date": date(2025, 6, 30),
        "book": create_book(),
        "user": params.get("user") or get_user_model().objects.create_user(
            email="test@user.com", password="test123user"
        )
    }
    defaults.update(params)
    if as_dict:
        defaults["book"] = defaults["book"].id
        del defaults["user"]
        return defaults
    return Borrowing.objects.create(**defaults)


class UnauthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.borrowing = create_borrowing()

    def test_unavailable_endpoints(self) -> None:
        responses = [
            self.client.get(BORROWING_URL),
            self.client.get(detail_url(self.borrowing.id)),
            self.client.post(BORROWING_URL),
            self.client.put(detail_url(self.borrowing.id)),
            self.client.delete(detail_url(self.borrowing.id))
        ]

        for response in responses:
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user_1 = get_user_model().objects.create_user(
            email="test_1@user.com", password="test123user"
        )
        self.user_2 = get_user_model().objects.create_user(
            email="test_2@user.com", password="test123user"
        )

        self.borrowing_1 = create_borrowing(user=self.user_1)
        self.borrowing_2 = create_borrowing(user=self.user_2)

        self.client.force_authenticate(self.user_1)

    def test_borrowing_list(self) -> None:
        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.filter(user_id=self.user_1.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_borrowing_detail(self) -> None:
        response = self.client.get(detail_url(self.borrowing_1.id))
        borrowing = Borrowing.objects.get(id=self.borrowing_1.id)
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_borrowing_create(self) -> None:
        payload = create_borrowing(as_dict=True)
        response = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["expected_return_date"], borrowing.expected_return_date)
        self.assertEqual(payload["book"], borrowing.book.id)
        self.assertEqual(self.user_1.id, borrowing.user.id)


class AdminUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="admin@user.com", password="test123user", is_staff=True
        )

        self.user_1 = get_user_model().objects.create_user(
            email="test_1@user.com", password="test123user"
        )
        self.user_2 = get_user_model().objects.create_user(
            email="test_2@user.com", password="test123user"
        )

        self.borrowing_1 = create_borrowing(user=self.user_1, is_active=True)
        self.borrowing_2 = create_borrowing(user=self.user_2, is_active=False)

        self.client.force_authenticate(self.admin_user)

    def test_borrowing_list(self) -> None:
        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingAdminListSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_filtering_borrowings_by_params(self) -> None:
        response_1 = self.client.get(BORROWING_URL, {"user_id": self.user_1.id})
        response_2 = self.client.get(BORROWING_URL, {"is_active": "true"})
        serializer_1 = BorrowingAdminListSerializer(self.borrowing_1)
        serializer_2 = BorrowingAdminListSerializer(self.borrowing_2)

        self.assertEqual(response_1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_2.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response_1.data["results"])
        self.assertIn(serializer_1.data, response_2.data["results"])
        self.assertNotIn(serializer_2.data, response_1.data["results"])
        self.assertNotIn(serializer_2.data, response_2.data["results"])

    def test_borrowing_detail(self) -> None:
        response = self.client.get(detail_url(self.borrowing_1.id))
        serializer = BorrowingAdminDetailSerializer(self.borrowing_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_borrowing_create(self) -> None:
        payload = create_borrowing(as_dict=True)
        response = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["expected_return_date"], borrowing.expected_return_date)
        self.assertEqual(payload["book"], borrowing.book.id)
        self.assertEqual(self.admin_user.id, borrowing.user.id)
