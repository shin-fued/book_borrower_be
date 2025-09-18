from typing import Optional
from urllib.request import Request
from django.http import HttpRequest
from django.utils import timezone
from books.serializers import GenreBookSerializer, GenreSerializer
from users.serializers import UserSerializer
from .serializers import (
    BookOrderSerializer,
    BookSerializer,
    TransactionsSerialiser,
    CategoryPriceSerializer,
)
from .models import Books, BooksUsersTransactions, CategoryPrice, Genre, GenreBook
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Users


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    lookup_field = "slug"


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = BooksUsersTransactions.objects.all()
    serializer_class = TransactionsSerialiser

    @action(
        detail=False, methods=["get"], url_path="borrower-books/(?P<username>[^/.]+)"
    )
    def borrower_books(
        self: "TransactionViewSet", request: Request, username: Optional[str] = None
    ) -> Response:
        borrower = get_object_or_404(Users, username=username)
        books = Books.objects.filter(transactions__user=borrower)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="book-borrowers/(?P<slug>[^/.]+)")
    def book_borrowers(
        self: "TransactionViewSet", request: Request, slug: Optional[str] = None
    ) -> Response:
        book = get_object_or_404(Books, slug=slug)
        borrowers = Users.objects.filter(transactions__book=book)
        serializer = UserSerializer(borrowers, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], url_path="borrow"
    )  # make transaction cost =  category price, make it so that one book can be borrowed once at a time
    def borrow_book(self: "TransactionViewSet", request: Request) -> Response:
        book_id = request.data.get("book")

        book = get_object_or_404(Books, pk=book_id)

        active_borrow = (
            BooksUsersTransactions.objects.filter(
                book_id=book_id,
            )
            .order_by("-created_at")
            .first()
            .transaction_type
            == "borrow"
        )

        if active_borrow:
            return Response({"error": "This book is already borrowed."}, status=400)

        price = book.category.price_per_day

        serializer = TransactionsSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(transaction_type="borrow", transaction_cost=price)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(
        detail=False, methods=["post"], url_path="return"
    )  # make the return transaction type calculated by days borrowed over 1
    def return_book(self: "TransactionViewSet", request: Request) -> Response:
        book_id = request.data.get("book")
        last_borrowed = (
            BooksUsersTransactions.objects.filter(
                book_id=book_id, user_id=request.data.get("user")
            )
            .order_by("-created_at")
            .first()
        )
        if not last_borrowed.transaction_type == "borrow":
            return Response(
                {"error": "No recent borrow record found for this book and user."},
                status=400,
            )
        book = get_object_or_404(Books, pk=book_id)
        price = book.category.price_per_day
        days_dued = (timezone.now().date() - last_borrowed.created_at.date()).days
        days_dued = max(1, days_dued)
        days_dued = int(days_dued) - 1
        serializer = TransactionsSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(
                transaction_type="return", transaction_cost=price * days_dued
            )
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    # paginaton filter, built in django rest framework
    # swagger api specs, use lib for gen
    # angular, for giving me a ui/look

    @action(
        detail=False,
        methods=["post"],
        url_path="book-orders/(?P<transaction_type>[^/.]+)",
    )
    def create_book_order(
        self: "TransactionViewSet",
        request: Request,
        transaction_type: Optional[str] = None,
    ) -> Response:
        serializer = BookOrderSerializer(
            data=request.data, context={"transaction_type": transaction_type}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()  # calls create()
        return Response(order)


class CategoryPriceViewSet(viewsets.ModelViewSet):
    queryset = CategoryPrice.objects.all()
    serializer_class = CategoryPriceSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreBookViewSet(viewsets.ModelViewSet):
    queryset = GenreBook.objects.all()
    serializer_class = GenreBookSerializer


# restrictions


# query first then struct, annotation django from queries, seperate view class such as book store stats
# think of how do i get order
