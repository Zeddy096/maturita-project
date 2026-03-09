from django.contrib import admin
from .models import Recipe

# Register your models here.

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "time_min")
    search_fields = ("name", "ingredients")