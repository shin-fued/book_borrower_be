from rest_framework import serializers
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
        fields = ['id', 'title', 'volume', 'condition', 'description', 'category', "genre", "slug", 'created_at', 'updated_at']
        
    def create(self, validated_data):
        genre_names = validated_data.pop('genre', [])
        book = Books.objects.create(**validated_data)
        
        for name in genre_names:
            genre_obj, _ = Genre.objects.get_or_create(name=name)
            GenreBook.objects.create(book=book, genre=genre_obj)
        
        return book
        

class TransactionsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = BooksUsersTransactions
        fields = ['id', 'book', 'user', 'transaction_time', 'transaction_type', 'transaction_cost']
        
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
        
