from django.db import models
from django.conf import settings
from django.db.models import Q, F

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gte=F("borrow_date")),
                name="expected_return_after_borrow"
            ),
            models.CheckConstraint(
                check=Q(actual_return_date__gte=F("borrow_date")),
                name="actual_return_after_borrow"
            )
        ]

    def __str__(self) -> str:
        return (f"{self.book.name} "
                f"({self.borrow_date} - "
                f"{self.expected_return_date})")
