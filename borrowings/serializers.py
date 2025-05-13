from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
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


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
        )


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookSerializer()


class BorrowingAdminListSerializer(BorrowingListSerializer):
    user = serializers.CharField(read_only=True, source="user.get_full_name")

    class Meta(BorrowingListSerializer.Meta):
        fields = BorrowingListSerializer.Meta.fields + ("user",)


class BorrowingAdminDetailSerializer(BorrowingAdminListSerializer):
    book = BookSerializer()
