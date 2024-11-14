from django.contrib import admin
from .models import AppUser, UserRole

admin.site.register(AppUser)
admin.site.register(UserRole)