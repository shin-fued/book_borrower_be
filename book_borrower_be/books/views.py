from .serializers import BookSerializer, TransactionsSerialiser
from .models import Books, Books_Users_Transactions
from rest_framework import viewsets

class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Books_Users_Transactions.objects.all()
    serializer_class = TransactionsSerialiser
