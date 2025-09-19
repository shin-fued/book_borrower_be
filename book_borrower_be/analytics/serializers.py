from rest_framework import serializers


class AnalyticsSerializer(serializers.Serializer):
    total_books = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    top_books = serializers.ListField(child=serializers.CharField())
    avg_borrow_days = serializers.CharField()


class UserActivitySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_borrows = serializers.IntegerField()
    total_returns = serializers.IntegerField()


class BookPopularitySerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    title = serializers.CharField()
    borrow_count = serializers.IntegerField()
    return_count = serializers.IntegerField()
    current_borrowers = serializers.CharField()
