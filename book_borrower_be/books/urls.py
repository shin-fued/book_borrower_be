from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CategoryPriceViewSet, GenreBookViewSet, GenreViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'genre', GenreViewSet)
router.register(r'genre-book', GenreBookViewSet)
router.register(r'category-price', CategoryPriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]