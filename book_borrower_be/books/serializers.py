from decimal import Decimal
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.utils import timezone
from users.models import Users
from .models import (
    Books,
    BooksUsersTransactions,
    CategoryPrice,
    Genre,
    GenreBook,
)


class BookSerializer(serializers.ModelSerializer):
    genre = serializers.ListField(child=serializers.CharField(), write_only=True)
    category = serializers.SlugRelatedField(
        queryset=CategoryPrice.objects.all(), slug_field="category"
    )

    class Meta:
        model = Books
        fields = [
            "id",
            "title",
            "volume",
            "condition",
            "description",
            "category",
            "genre",
            "updated_at",
            "slug",
            "author",
        ]

    def create(self: Books, validated_data: Books) -> Books:
        genre_names = validated_data.pop("genre", [])
        book = Books.objects.create(**validated_data)

        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(name=name)
            GenreBook.objects.create(book=book, genre=genre_obj)

        return book


class TransactionsSerialiser(serializers.ModelSerializer):
    transaction_type = serializers.CharField(read_only=True)
    transaction_cost = serializers.DecimalField(
        read_only=True, max_digits=6, decimal_places=2
    )

    class Meta:
        model = BooksUsersTransactions
        fields = [
            "id",
            "book",
            "user",
            "updated_at",
            "transaction_type",
            "transaction_cost",
        ]


class CategoryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPrice
        fields = ["id", "category", "price_per_day"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class GenreBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreBook
        fields = ["id", "genre", "book"]


class BookOrderItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()


class BookOrderSerializer(serializers.Serializer):
    username = serializers.CharField()
    books = BookOrderItemSerializer(many=True)
    transactions = TransactionsSerialiser(many=True, read_only=True)
    transaction_type = serializers.CharField(read_only=True)
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    def borrow_pricing(self: "BookOrderSerializer", book: Books, user_id: int) -> float:
        active_borrow = (
            BooksUsersTransactions.objects.filter(
                book_id=book.id,
            )
            .order_by("-created_at")
            .first()
        )
        if active_borrow and active_borrow.transaction_type == "borrow":
            raise ValidationError(f"Book (id={book.id}) is already borrowed.")
        return book.category.price_per_day

    def return_pricing(self: "BookOrderSerializer", book: Books, user_id: int) -> float:
        last_borrowed = (
            BooksUsersTransactions.objects.filter(book_id=book.id, user_id=user_id)
            .order_by("-created_at")
            .first()
        )
        if not last_borrowed.transaction_type == "borrow":
            raise ValidationError(
                f"Book (id={book.id}) is not currently borrowed by user (id={user_id})."
            )
        price = book.category.price_per_day
        days_dued = (timezone.now().date() - last_borrowed.created_at.date()).days
        days_dued = max(1, days_dued)
        days_dued = int(days_dued) - 1
        return price * days_dued

    def validate_books(
        self: "BookOrderSerializer", books_data: list[dict]
    ) -> list[dict]:
        if not books_data:
            raise serializers.ValidationError("At least one book must be provided.")

        validated_books = []
        for book_dict in books_data:
            book_serializer = BookOrderItemSerializer(data=book_dict)
            book_serializer.is_valid(raise_exception=True)  # validate this single book
            validated_books.append(book_serializer.validated_data)

        return validated_books

    def create(
        self: "BookOrderSerializer", validated_data: dict[str, any]
    ) -> dict[str, any]:
        validated_books = validated_data["books"]
        username: str = validated_data["username"]
        user: Users = get_object_or_404(Users, username=username)
        transaction_type: str = self.context.get("transaction_type", "borrow")

        transactions: list[BooksUsersTransactions] = []
        total_cost = Decimal("0.0")

        transaction_pricing = (
            self.return_pricing if transaction_type == "return" else self.borrow_pricing
        )

        for book_data in validated_books:
            book_id: int = book_data["book_id"]
            book: Books = get_object_or_404(Books, pk=book_id)
            price = transaction_pricing(book, user.id)

            txn: BooksUsersTransactions = BooksUsersTransactions.objects.create(
                book_id=book_id,
                user_id=user.id,
                transaction_type=transaction_type,
                transaction_cost=price,
            )
            transactions.append(txn)
            total_cost += txn.transaction_cost

        validated_data["transactions"] = TransactionsSerialiser(
            transactions, many=True
        ).data
        validated_data["total_cost"] = total_cost
        validated_data["transaction_type"] = transaction_type

        return validated_data

    # should i have a resolved seperate field to see what books are borrowed and not return
