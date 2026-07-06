# Register your models here.
from django.contrib import admin

from user_reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = []
