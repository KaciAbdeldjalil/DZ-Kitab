from django.db import models

class Annonce(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='annonces/', null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.isbn})"
