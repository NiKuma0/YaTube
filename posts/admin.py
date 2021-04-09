from django.contrib import admin

from .models import Follow, Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "pk")
    search_fields = ("title",)
    empty_value_display = "-пусто-"
    prepopulated_fields = {"slug": ("title",)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "text", "author", "created")
    search_fields = ("text", "post")
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    search_fields = ("author",)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
