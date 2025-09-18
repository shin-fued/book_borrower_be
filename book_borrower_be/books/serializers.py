from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.models import Users
from .models import Books, BooksUsersTransactions, CategoryPrice, Genre, GenreBook

class BookSerializer(serializers.ModelSerializer):
    genre = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    category = serializers.SlugRelatedField(
        queryset=CategoryPrice.objects.all(),
        slug_field='category'
    )
    class Meta:
        model = Books
        fields = ['id', 'title', 'volume', 'condition', 'description', 'category', "genre", "updated_at", "slug"]
        
    def create(self, validated_data):
        genre_names = validated_data.pop('genre', [])
        book = Books.objects.create(**validated_data)
        
        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(name=name)
            GenreBook.objects.create(book=book, genre=genre_obj)
        
        return book
        

class TransactionsSerialiser(serializers.ModelSerializer):
    transaction_type = serializers.CharField(read_only=True)
    transaction_cost = serializers.DecimalField(read_only=True, max_digits=6, decimal_places=2)
    class Meta:
        model = BooksUsersTransactions
        fields = ['id', 'book', 'user', 'updated_at', 'transaction_type', 'transaction_cost']
        
class CategoryPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPrice
        fields = ['id', 'category', 'price_per_day']
        
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'genre']
        
class GenreBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenreBook
        fields = ['id', 'genre', 'book']
        
class BookOrderItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    
class BookOrderSerializer(serializers.Serializer):
    username = serializers.CharField()
    books = BookOrderItemSerializer(many=True)
    transactions = TransactionsSerialiser(many=True, read_only=True)
    transaction_type = serializers.CharField(read_only=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def create(self, validated_data):
        username = validated_data['username']
        user = get_object_or_404(Users, username=username)
        transaction_type = self.context.get('transaction_type')
    
        books_data = validated_data['books']
        transactions = []
        total_cost = 0
    
        for book_data in books_data:
            book_id = book_data['book_id']
            book = get_object_or_404(Books, pk=book_id)
            price = book.category.price_per_day
        
            txn = BooksUsersTransactions.objects.create(
                book_id=book_id,
                user_id=user.id,
                transaction_type=transaction_type,
                transaction_cost=price
            )
            transactions.append(txn)
            total_cost += txn.transaction_cost

        validated_data['transactions'] = TransactionsSerialiser(transactions, many=True).data
        validated_data['total_cost'] = total_cost
        validated_data['transaction_type'] = transaction_type
    
        return validated_data
