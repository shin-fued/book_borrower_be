from django.db import models
from users.views import Users
from django.utils.text import slugify
from django.core.validators import MinValueValidator

from base_models.models import BaseModel


# Create your models here.


class CategoryPrice(models.Model):
    class CategoriesType(models.TextChoices):
        MANGA = "manga", "Manga"
        COMICS = "comics", "Comics"
        NON_FICTION = "non-fiction", "Non-Fiction"
        EDUCATIONAL = "educational", "Educational"
        MAGAZINE = "magazine", "Magazine"
        NOVEL = "novel", "Novel"

    category = models.CharField(
        max_length=20,
        choices=CategoriesType.choices,
        unique=True,
    )
    price_per_day = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(0.0)]
    )


class Genre(models.Model):
    name = models.CharField(max_length=50)


class Books(BaseModel):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    author = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    category = models.ForeignKey(CategoryPrice, on_delete=models.CASCADE)
    volume = models.IntegerField(default=1)

    def save(self: "Books", *args: object, **kwargs: object) -> None:
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


# make pricing based on something ie a new field such as type

# make new model for stats etc


class BooksUsersTransactions(BaseModel):
    class TransactionTypes(models.TextChoices):
        BORROW = "borrow", "Borrow"
        RETURN = "return", "Return"

    book = models.ForeignKey(
        Books, on_delete=models.DO_NOTHING, related_name="transactions"
    )
    user = models.ForeignKey(
        Users, on_delete=models.DO_NOTHING, related_name="transactions"
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionTypes.choices,
    )
    transaction_cost = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]
