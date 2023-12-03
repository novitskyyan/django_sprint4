from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from .models import Post, Category, Location, Comment

admin.site.register(Category)
admin.site.register(Location)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'location',
        'category',
        'comment_count'
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(comment_count=Count('comment'))

    def comment_count(self, obj):
        return obj.comment_count

    comment_count.short_description = 'Количество комментариев'

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.image.url}">')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'created_at',
        'author'
    )
