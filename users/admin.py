from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        )
    # define fields
    all_fields = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
                )
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        # ('Additional info', {
        #     'fields': ('test',)
        # })
    )
    # add fields to user creation and user detail in admin panel
    add_fieldsets = all_fields
    fieldsets = all_fields

admin.site.register(CustomUser, CustomUserAdmin)