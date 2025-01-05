from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin
from allauth.account.models import EmailAddress

# Customize the admin section for CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'role', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

    def email_verified(self, obj):
        email = EmailAddress.objects.filter(user=obj).first()
        return email.verified if email else False
    email_verified.boolean = True
    email_verified.short_description = 'Email Verified'

    list_display += ('email_verified',)
