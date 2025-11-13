from django.contrib import admin
from .models import (
    Category, Product, ProductReview,
    ReviewReply, ReviewHelpfulVote
)


# =========================
# INLINE ADMIN CLASSES
# =========================

class SubCategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1
    show_change_link = True


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 0
    readonly_fields = ('user', 'rating', 'title', 'content', 'created_at')


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply
    extra = 0
    readonly_fields = ('user', 'content', 'created_at')


# =========================
# CATEGORY ADMIN
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('parent',)
    inlines = [SubCategoryInline]


# =========================
# PRODUCT ADMIN
# =========================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'seller', 'category', 'price',
        'stock', 'is_active', 'created_at'
    )
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('name', 'description', 'seller__username')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductReviewInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Basic Info", {
            'fields': ('name', 'slug', 'seller', 'category', 'description', 'image')
        }),
        ("Inventory & Pricing", {
            'fields': ('price', 'stock', 'is_active')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )


# =========================
# PRODUCT REVIEW ADMIN
# =========================
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product', 'user', 'rating', 'is_verified',
        'created_at', 'updated_at'
    )
    list_filter = ('rating', 'is_verified', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'content')
    inlines = [ReviewReplyInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Review Info", {
            'fields': ('product', 'user', 'rating', 'title', 'content', 'image')
        }),
        ("Verification", {
            'fields': ('is_verified',)
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )


# =========================
# REVIEW REPLY ADMIN
# =========================
@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'created_at')
    search_fields = ('review__product__name', 'user__username', 'content')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)


# =========================
# HELPFUL VOTE ADMIN
# =========================
@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    search_fields = ('review__product__name', 'user__username')
    list_filter = ('is_helpful', 'created_at')
    readonly_fields = ('created_at',)
