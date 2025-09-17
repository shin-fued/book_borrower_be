from users.serializers import UserSerializer
from .serializers import BookSerializer, TransactionsSerialiser
from .models import Books, Books_Users_Transactions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Users

class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Books_Users_Transactions.objects.all()
    serializer_class = TransactionsSerialiser
    
    @action(detail=True, methods=['get'], url_path='borrower-books')
    def borrower_books(self, request, pk=None):
        borrower = get_object_or_404(Users, pk=pk)
        books = Books.objects.filter(transactions__user=borrower)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='book-borrowers')
    def book_borrowers(self, request, pk=None):
        book = get_object_or_404(Books, pk=pk)
        borrowers = Users.objects.filter(transactions__book=book)
        serializer = UserSerializer(borrowers, many=True)
        return Response(serializer.data)
