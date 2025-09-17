from django.db import models
from users.views import Users
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator

# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) #make it update if you call put or patch
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set created_at during the first save
            self.created_at = timezone.now()
        self.updated_at = timezone.now()  # Update updated_at on every save
        super().save(*args, **kwargs)
        
class CategoryPrice(models.Model):
    category = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2,validators=[MinValueValidator(0.0)])  # e.g., 1.00 for standard, 1.50 for premium
    
class Genre(models.Model):
    name = models.CharField(max_length=50)
    
class Books(BaseModel):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    condition = models.CharField(max_length=50)
    genre = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    category = models.ForeignKey(CategoryPrice, on_delete=models.CASCADE)
    volume = models.IntegerField(default=1)
    def save(self, *args, **kwargs):
        if not self.slug:  # only create slug on first save
            base_slug = f"{slugify(self.title)}-v{self.volume}"
            slug = base_slug
            counter = 1
            while Books.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
class GenreBook(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    
    
#make pricing based on something ie a new field such as type

#make new model for stats etc

class BooksUsersTransactions(models.Model):
    book = models.ForeignKey(Books, on_delete=models.DO_NOTHING, related_name='transactions')
    user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, related_name='transactions')
    transaction_type = models.CharField(max_length=50)  # e.g., 'borrow', 'return'
    transaction_cost = models.DecimalField(max_digits=6, decimal_places=2)

