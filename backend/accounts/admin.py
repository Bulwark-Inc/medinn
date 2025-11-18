from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, AuditLog, PendingEmailChange


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'is_seller', 'email_verified', 'is_active', 'is_deleted', 'date_joined')
    list_filter = ('is_seller', 'email_verified', 'is_active', 'is_deleted', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('email_verified', 'is_deleted', 'deleted_at')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_seller'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'deleted_at')
    
    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Full Name'

    actions = ['activate_users', 'deactivate_users', 'verify_emails', 'soft_delete_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True, is_deleted=False)
        self.message_user(request, f"{queryset.count()} user(s) activated successfully.")
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} user(s) deactivated successfully.")
    deactivate_users.short_description = "Deactivate selected users"

    def verify_emails(self, request, queryset):
        queryset.update(email_verified=True)
        self.message_user(request, f"{queryset.count()} email(s) verified successfully.")
    verify_emails.short_description = "Verify selected user emails"

    def soft_delete_users(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_deleted=True, is_active=False, deleted_at=timezone.now())
        self.message_user(request, f"{queryset.count()} user(s) soft deleted successfully.")
    soft_delete_users.short_description = "Soft delete selected users"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'event_type', 'ip_address', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'ip_address', 'event_type')
    readonly_fields = ('user', 'event_type', 'ip_address', 'user_agent', 'details', 'timestamp')
    ordering = ('-timestamp',)
    
    def user_email(self, obj):
        return obj.user.email if obj.user else 'N/A'
    user_email.short_description = 'User Email'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PendingEmailChange)
class PendingEmailChangeAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_email', 'created_at', 'expires_at', 'is_expired_status')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email', 'new_email')
    readonly_fields = ('user', 'new_email', 'token', 'created_at', 'expires_at')
    ordering = ('-created_at',)
    
    def is_expired_status(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_status.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False