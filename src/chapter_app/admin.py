from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Chapter, Summary

admin.site.register(Chapter)
admin.site.register(Summary)


@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)

