from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.utils import timezone
from users.models import Users
from .models import Books, BooksUsersTransactions, CategoryPrice, Genre, GenreBook


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
        ]

    def create(self, validated_data):
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
        fields = ["id", "genre"]


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

    def borrow_pricing(book, user_id):
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

    def return_pricing(book, user_id) -> float:
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

    # precommit
    def validate_books(
        self, books
    ):  # gets called before create update, validatebefore create, if test create
        if not value:
            raise serializers.ValidationError("At least one book must be provided.")
        return value

    def create(self, validated_data):
        username = validated_data["username"]
        user = get_object_or_404(Users, username=username)
        transaction_type = self.context.get("transaction_type")

        books_data = validated_data["books"]
        transactions = []
        total_cost = 0

        if transaction_type == "return":
            transaction_pricing = return_pricing  # TODO call this
        else:
            transaction_pricing = borrow_pricing

        for book_data in books_data:
            book_id = book_data["book_id"]
            book = get_object_or_404(Books, pk=book_id)
            price = transaction_pricing(book, user.id)

            txn = BooksUsersTransactions.objects.create(
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
