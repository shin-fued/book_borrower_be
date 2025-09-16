from .serializers import BookSerializer
from .models import Books
from rest_framework import viewsets

class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BookSerializer

# Create your views here.
