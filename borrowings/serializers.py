from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        )

    def validate(self, attrs):
        if attrs["book"].inventory == 0:
            raise ValidationError("This book is out of stock.")
        return attrs
