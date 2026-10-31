from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rooms.forms import CustomUserCreationForm, CustomUserChangeForm
from rooms.models import User, Room

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ["email", "username", "date_joined", "is_superuser"]

admin.site.register(User, CustomUserAdmin)
admin.site.register(Room)
