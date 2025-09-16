from django.db import models

# Create your models here.
class Books(models.Model):
  title = models.CharField(max_length=50, unique=True)
  description = models.CharField(max_length=255)
  price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
  condition = models.CharField(max_length=50)
  genre = models.CharField(max_length=50)
  added_at = models.DateTimeField(auto_now_add=True)