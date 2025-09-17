from django.db import models
from django.utils import timezone

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