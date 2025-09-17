from django.db import models
from users.views import Users

# Create your models here.
class Books(models.Model):
  title = models.CharField(max_length=50, unique=True)
  description = models.CharField(max_length=255)
  price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
  condition = models.CharField(max_length=50)
  genre = models.CharField(max_length=50)
  added_at = models.DateTimeField(auto_now_add=True)

class Books_Users_Transactions(models.Model):
    book = models.ForeignKey(Books, on_delete=models.DO_NOTHING, related_name='transactions')
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='transactions')
    transaction_time = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=50)  # e.g., 'borrow', 'return'
    transaction_cost = models.DecimalField(max_digits=6, decimal_places=2)

