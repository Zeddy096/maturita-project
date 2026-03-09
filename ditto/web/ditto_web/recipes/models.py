from django.db import models

# Create your models here.
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    time_min = models.IntegerField(null=True, blank=True)
    ingredients = models.TextField()
    steps = models.TextField()
    image = models.ImageField(upload_to="recipes/", null=True, blank=True)

    def __str__(self):
        return self.name