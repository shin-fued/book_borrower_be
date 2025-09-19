from itertools import count
from typing import Optional
from urllib.request import Request
from rest_framework import viewsets
from django.db.models import Sum
from books.models import Books, BooksUsersTransactions
from users.models import Users
from .serializers import (
    AnalyticsSerializer,
    BookPopularitySerializer,
    UserActivitySerializer,
)
from rest_framework.response import Response


# Create your views here.
class AnalyticsViewSet(viewsets.ViewSet):
    serializer_class = AnalyticsSerializer

    def list(
        self: "AnalyticsViewSet", request: Request, *args: object, **kwargs: object
    ) -> Response:
        # query from database to get analytics data, select sum(transaction_cost), top(book).titles, count(rows), avg(borrow-return day for same transaction) from transactions,
        transactions = BooksUsersTransactions.objects.all()
        total_revenue = (
            transactions.aggregate(total=Sum("transaction_cost"))["total"] or 0
        )
        transaction_count = transactions.count()
        transactions = transactions.values(
            "transaction_type",
            "book_id",
            "user_id",
            "created_at",
        ).order_by("created_at")

        # Average borrow duration calculation
        borrow_durations = []
        borrow_dict = {}
        for t in transactions:
            if t["transaction_type"] == "borrow":
                borrow_dict[(t["user_id"], t["book_id"])] = t
            elif t["transaction_type"] == "return":
                borrow_key = (t["user_id"], t["book_id"])
                if borrow_key in borrow_dict:
                    borrow_durations.append(
                        (t["created_at"] - borrow_dict[borrow_key]["created_at"]).days
                    )
                    del borrow_dict[borrow_key]

        avg_borrow_days = (
            sum(borrow_durations) / len(borrow_durations) if borrow_durations else 0
        )

        # Top books by number of transactions
        top_books_qs = (
            transactions.values("book")
            .annotate(count=count("id"))
            .order_by("-count")[:5]
        )

        top_books = [
            {
                "title": Books.objects.get(id=b["book"]).title,
                "count": b["count"],
                "volume": Books.objects.get(id=b["book"]).volume,
            }
            for b in top_books_qs
        ]

        # Counts for users and books
        total_users = Users.objects.count()
        total_books = Books.objects.count()

        data = {
            "total_revenue": total_revenue,
            "total_transactions": transaction_count,
            "avg_borrow_days": avg_borrow_days,
            "top_books": list(top_books),
            "total_users": total_users,
            "total_books": total_books,
        }
        serializer = self.serializer_class(instance=data)
        return Response(serializer.data)


class UserActivityViewSet(viewsets.ViewSet):
    serializer_class = UserActivitySerializer

    def retrieve(
        self: "UserActivityViewSet",
        request: Request,
        pk: Optional[str] = None,
        *args: object,
        **kwargs: object
    ) -> Response:
        user = Users.objects.get(username=pk)
        transactions = BooksUsersTransactions.objects.filter(user_id=user.id)
        total_borrows = transactions.filter(transaction_type="borrow").count()
        total_returns = transactions.filter(transaction_type="return").count()

        data = {
            "user_id": user.id,
            "username": user.username,
            "total_borrows": total_borrows,
            "total_returns": total_returns,
        }
        serializer = self.serializer_class(instance=data)
        return Response(serializer.data)


class BookPopularityViewSet(viewsets.ViewSet):
    serializer_class = BookPopularitySerializer

    def retrieve(
        self: "BookPopularityViewSet",
        request: Request,
        pk: Optional[str] = None,
        *args: object,
        **kwargs: object
    ) -> Response:
        book = Books.objects.get(slug=pk)
        transactions = BooksUsersTransactions.objects.filter(book_id=book.id)
        borrow_count = transactions.filter(transaction_type="borrow").count()
        return_count = transactions.filter(transaction_type="return").count()

        current_borrower = "No current borrower"
        for t in transactions:
            if t.transaction_type == "borrow":
                current_borrower = Users.objects.get(id=t.user_id).username
            elif t.transaction_type == "return":
                current_borrower = "No current borrower"

        data = {
            "book_id": book.id,
            "title": book.title,
            "borrow_count": borrow_count,
            "return_count": return_count,
            "current_borrowers": current_borrower,
        }
        serializer = self.serializer_class(instance=data)
        return Response(serializer.data)
