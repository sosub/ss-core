from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    SPONSOR = 'SP'
    MEMBER = 'ME'
    POSTER = 'PO'
    MODERATOR = 'MO'
    ADMINISTRATOR = 'AD'

    ROLES = {
        SPONSOR: 'Sponsor',
        MEMBER: 'Member',
        POSTER: 'Poster',
        MODERATOR: 'Moderator',
        ADMINISTRATOR: 'Administrator',
    }

    ROLE_CHOICES = (
        (SPONSOR, 'Sponsor'),
        (MEMBER, 'Member'),
        (POSTER, 'Poster'),
        (MODERATOR, 'Moderator'),
        (ADMINISTRATOR, 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=255, blank=True)
    cover = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    quote = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=255, blank=True)
    birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default='MB')

    def __str__(self):
        return self.user.username


class Menu(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    tooltip = models.CharField(max_length=255)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.name


class Source(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    image = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.CharField(max_length=255)

    video_id = models.CharField(max_length=255)
    duration = models.IntegerField()

    vi_sub = models.CharField(max_length=255)
    en_sub = models.CharField(max_length=255)
    vi_transcript = models.TextField(blank=True)
    en_transcript = models.TextField(blank=True)
    
    view_amount = models.IntegerField(default=0)

    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_created_by')
    published_at = models.DateTimeField(null=True)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='video_published_by')
    updated_at = models.DateTimeField(null=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='video_updated_by')
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, blank=True, null=True)
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='video_sponsor_by')

    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Speaker(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class VideoSpeaker(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, )
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, )

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = (('video', 'speaker'),)


class Category(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class VideoCategory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = (('video', 'category'),)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "SubCategories"
        unique_together = (('category', 'slug'),)
        

class VideoSubCategory(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = (('video', 'subcategory'),)


class Tag(models.Model):
    slug = models.CharField(max_length=255)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    def __str__(self):
        return self.slug

    class Meta:
        unique_together = (('slug', 'video'),)
        
        
class Playlist(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255)

    def __str__(self):
        return self.name
        
        
class PlaylistVideo(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = (('playlist', 'video'),)
