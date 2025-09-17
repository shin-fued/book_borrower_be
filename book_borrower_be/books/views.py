from books.serializers import GenreBookSerializer, GenreSerializer
from users.serializers import UserSerializer
from .serializers import BookSerializer, TransactionsSerialiser, CategoryPriceSerializer
from .models import Books, BooksUsersTransactions, CategoryPrice, Genre, GenreBook
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from users.models import Users

class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'slug'
    

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = BooksUsersTransactions.objects.all()
    serializerClass = TransactionsSerialiser
    
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
    
    @action(detail=True, methods=['post'], url_path='borrow')
    def borrow(self, request):
        serializer = TransactionsSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(transaction_type='borrow')
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
    @action(detail=True,methods=['post'],url_path='return')
    def borrow(self, request):
        serializer = TransactionsSerialiser(data=request.data)
        if serializer.is_valid():
            serializer.save(transaction_type='return')
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    #TODO: url_path = transactions/borrow and return make set type
    
class CategoryPriceViewSet(viewsets.ModelViewSet):
    queryset = CategoryPrice.objects.all()
    serializer_class = CategoryPriceSerializer
    
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    
class GenreBookViewSet(viewsets.ModelViewSet):
    queryset = GenreBook.objects.all()
    serializer_class = GenreBookSerializer
    
#restrictions


#query first then struct, annotation django from queries, seperate view class such as book store stats