from django.contrib import admin
from . import models
from django.contrib.admin.models import LogEntry

class VideoSpeakerInline(admin.TabularInline):
    model = models.VideoSpeaker
    extra = 0
    
class VideoCategoryInline(admin.TabularInline):
    model = models.VideoCategory
    extra = 0
    
class VideoSubCategoryInline(admin.TabularInline):
    model = models.VideoSubCategory
    extra = 0
    
class TagInline(admin.TabularInline):
    model = models.Tag
    extra = 0
    
class PlaylistVideoInline(admin.TabularInline):
    model = models.PlaylistVideo
    extra = 0

class VideoAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title', 'source', 'is_published', 'view_amount')
    list_filter = ('is_published', 'source', 'sponsor')
    search_fields = ['title', 'description', 'source__name']
        
    inlines = [
        VideoSpeakerInline,
        VideoCategoryInline,
        VideoSubCategoryInline,
        TagInline,
        PlaylistVideoInline,
    ]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullname', 'email', 'role')
    list_filter = ('role',)
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']

    def email(self, instance):
        return instance.user.email

    def fullname(self, instance):
        return instance.user.get_full_name()


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'priority')


class SubCategoryInline(admin.TabularInline):
    model = models.SubCategory
    extra = 0

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority',)
    
    inlines = [
        SubCategoryInline,
    ]


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'priority',)
    list_filter = ('category', )


class PlaylistAdmin(admin.ModelAdmin):
    inlines = [
        PlaylistVideoInline,
    ]


admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Profile, ProfileAdmin)
admin.site.register(models.Menu, MenuAdmin)

admin.site.register(models.Source)
admin.site.register(models.Speaker)

admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.SubCategory, SubCategoryAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Playlist, PlaylistAdmin)
admin.site.register(LogEntry)
