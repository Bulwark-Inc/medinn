from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Address, NotificationPreference, SellerProfile, ProfileAuditLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'phone_number', 'has_avatar', 'completion_percentage', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'completion_percentage_display', 'avatar_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Information', {'fields': ('phone_number', 'date_of_birth', 'bio')}),
        ('Avatar', {'fields': ('avatar', 'avatar_preview')}),
        ('Metadata', {'fields': ('completion_percentage_display', 'created_at', 'updated_at')}),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def has_avatar(self, obj):
        if obj.avatar:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_avatar.short_description = 'Avatar'
    
    def completion_percentage(self, obj):
        percentage = obj.get_completion_percentage()
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color,
            percentage
        )
    completion_percentage.short_description = 'Completion'
    
    def completion_percentage_display(self, obj):
        return f"{obj.get_completion_percentage()}%"
    completion_percentage_display.short_description = 'Profile Completion'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="100" height="100" />', obj.avatar.url)
        return "No avatar"
    avatar_preview.short_description = 'Avatar Preview'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user_email', 'address_type', 'is_default', 'city', 'state', 'created_at')
    list_filter = ('address_type', 'is_default', 'country', 'created_at')
    search_fields = ('user__email', 'full_name', 'city', 'state', 'postal_code')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Address Type', {'fields': ('address_type', 'is_default')}),
        ('Contact Information', {'fields': ('full_name', 'phone_number')}),
        ('Address Details', {'fields': ('street_address', 'apartment', 'city', 'state', 'postal_code', 'country')}),
        ('Additional Info', {'fields': ('delivery_instructions',)}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    actions = ['set_as_default', 'unset_as_default']
    
    def set_as_default(self, request, queryset):
        for address in queryset:
            # Unset other defaults of same type
            Address.objects.filter(
                user=address.user,
                address_type=address.address_type
            ).update(is_default=False)
            # Set this as default
            address.is_default = True
            address.save()
        self.message_user(request, f"{queryset.count()} address(es) set as default.")
    set_as_default.short_description = "Set selected addresses as default"
    
    def unset_as_default(self, request, queryset):
        queryset.update(is_default=False)
        self.message_user(request, f"{queryset.count()} address(es) unset as default.")
    unset_as_default.short_description = "Unset selected addresses as default"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'order_updates', 'promotions', 'newsletter', 'seller_updates', 'updated_at')
    list_filter = ('order_updates', 'promotions', 'newsletter', 'seller_updates')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('General Notifications', {'fields': ('order_updates', 'promotions', 'product_restocked', 'newsletter')}),
        ('Seller Notifications', {'fields': ('seller_updates', 'new_orders', 'low_stock_alerts')}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user_email', 'is_active', 'has_logo', 'has_banner', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('store_name', 'store_slug', 'user__email')
    readonly_fields = ('store_slug', 'created_at', 'updated_at', 'logo_preview', 'banner_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Store Information', {'fields': ('store_name', 'store_slug', 'store_description', 'is_active')}),
        ('Store Images', {'fields': ('store_logo', 'logo_preview', 'store_banner', 'banner_preview')}),
        ('Policies', {'fields': ('return_policy', 'shipping_policy')}),
        ('Metadata', {'fields': ('created_at', 'updated_at')}),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def has_logo(self, obj):
        if obj.store_logo:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_logo.short_description = 'Logo'
    
    def has_banner(self, obj):
        if obj.store_banner:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_banner.short_description = 'Banner'
    
    def logo_preview(self, obj):
        if obj.store_logo:
            return format_html('<img src="{}" width="100" height="100" />', obj.store_logo.url)
        return "No logo"
    logo_preview.short_description = 'Logo Preview'
    
    def banner_preview(self, obj):
        if obj.store_banner:
            return format_html('<img src="{}" width="300" height="100" />', obj.store_banner.url)
        return "No banner"
    banner_preview.short_description = 'Banner Preview'
    
    actions = ['activate_stores', 'deactivate_stores']
    
    def activate_stores(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} store(s) activated.")
    activate_stores.short_description = "Activate selected stores"
    
    def deactivate_stores(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} store(s) deactivated.")
    deactivate_stores.short_description = "Deactivate selected stores"


@admin.register(ProfileAuditLog)
class ProfileAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'event_type', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'event_type')
    readonly_fields = ('user', 'event_type', 'details', 'timestamp')
    ordering = ('-timestamp',)
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False