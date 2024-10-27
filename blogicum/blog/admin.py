from django.contrib import admin

from .models import Category, Comment, Location, Post


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Админка для локаций."""

    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий."""

    list_display = ('title', 'is_published', 'created_at')
    list_editable = ('is_published',)
    search_fields = ('title',)
    list_filter = ('is_published', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админка для комментариев."""

    list_display = ('author', 'post', 'text', 'created_at')
    search_fields = ('author__username', 'post__title', 'text')
    list_filter = ('created_at', 'post')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка для постов."""

    list_display = (
        'title',
        'is_published',
        'category',
        'author',
        'location',
        'text',
        'pub_date',
        'created_at',
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category', 'is_published', 'pub_date',)
    list_display_links = ('title',)
