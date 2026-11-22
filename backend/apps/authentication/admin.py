from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'cargo', 'is_staff', 'is_active')
    list_filter = ('cargo', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Corporativas E-Service', {
            'fields': ('cargo', 'telefone', 'avatar'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Corporativas E-Service', {
            'fields': ('cargo', 'telefone', 'avatar'),
        }),
    )
