from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from django.test import TestCase
from django.urls import reverse

from borrowings.models import Borrowing
from books.tests import create_book


BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id: int) -> Response:
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


def create_borrowing(as_dict: bool=False, **params):
    defaults = {
        "expected_return_date": datetime(2025, 6, 30),
        "book": create_book(),
        "user": get_user_model().objects.create_user(
            email="test@user.com", password="test123user"
        )
    }
    defaults.update(params)
    return defaults if as_dict else Borrowing.objects.create(**defaults)


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
