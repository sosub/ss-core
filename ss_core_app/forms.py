from django import forms
from django.contrib.auth.models import User
from . import models


class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = (
            'slug', 
            'title', 
            'description', 
            'image', 
            'video_id',
            'duration',
            'vi_sub',
            'en_sub',
            'vi_transcript',
            'en_transcript',
            'source',
            'sponsor',
        )


class VideoImportForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = (
            'slug', 
            'title', 
            'description', 
            'image', 
            'video_id',
            'duration',
            'vi_sub',
            'en_sub',
            'vi_transcript',
            'en_transcript',
            'view_amount',
            'is_published',
            'created_at',
            'created_by',
            'published_at',
            'published_by',
            'source',
            'sponsor',
        )


class VideoSpeakerForm(forms.ModelForm):
    class Meta:
        model = models.VideoSpeaker
        fields = (
            'video', 
            'speaker', 
        )


class VideoCategoryForm(forms.ModelForm):
    class Meta:
        model = models.VideoCategory
        fields = (
            'video', 
            'category', 
        )


class VideoSubCategoryForm(forms.ModelForm):
    class Meta:
        model = models.VideoSubCategory
        fields = (
            'video', 
            'subcategory', 
        )


class TagForm(forms.ModelForm):
    class Meta:
        model = models.Tag
        fields = (
            'video', 
            'slug', 
        )


class SourceForm(forms.ModelForm):
    class Meta:
        model = models.Source
        fields = (
            'slug', 
            'name', 
            'description', 
            'image', 
        )


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = models.Speaker
        fields = (
            'slug', 
            'name', 
            'description', 
            'image', 
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = (
            'slug', 
            'name', 
            'description', 
            'image', 
            'priority', 
        )

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = models.SubCategory
        fields = (
            'category',
            'slug',
            'name', 
            'description', 
            'image',
            'priority',
        )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name', 
            'email',
        )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = (
            'user',
            'role',
            'avatar',
            'cover',
            'quote',
            'bio',
            'facebook',
            'website',
        )

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = models.Playlist
        fields = (
            'slug', 
            'name', 
            'description', 
            'image', 
        )


class PlaylistVideoForm(forms.ModelForm):
    class Meta:
        model = models.PlaylistVideo
        fields = (
            'playlist', 
            'video', 
            'priority', 
        )