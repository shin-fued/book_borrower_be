from rest_framework import serializers
from .models import Books, Books_Users_Transactions

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ['id', 'title', 'price_per_day', 'genre', 'added_at', 'condition', 'description']

class TransactionsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Books_Users_Transactions
        fields = ['id', 'book', 'user', 'transaction_time', 'transaction_type', 'transaction_cost']
        
