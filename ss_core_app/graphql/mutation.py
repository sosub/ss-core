import graphene
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from .. import models, forms
from ..utils import name_to_slug, get_permission
from . import query

class CreateVideo(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        title = graphene.String()
        description = graphene.String()
        image = graphene.String()
        video_id = graphene.String()
        duration = graphene.Int()
        vi_sub = graphene.String()
        en_sub = graphene.String()
        vi_transcript = graphene.String(default_value="")
        en_transcript = graphene.String(default_value="")
        source_id = graphene.String(default_value="")
        sponsor_id = graphene.String(default_value="")
        speaker_ids = graphene.List(graphene.String, default_value=[])
        category_ids = graphene.List(graphene.String, default_value=[])
        subcategory_ids = graphene.List(graphene.String, default_value=[])
        tags = graphene.List(graphene.String, default_value=[])

    video = graphene.Field(query.Video, slug=graphene.String())

    def mutate(self, info, slug, title, description, image, video_id, duration, vi_sub, en_sub, 
        vi_transcript, en_transcript, source_id, sponsor_id, speaker_ids, category_ids, subcategory_ids, tags):
        user = info.context.user

        if not get_permission('create_video', user):
            raise Exception("Permission denied.")

        with transaction.atomic():
            video_form = forms.VideoForm({
                "slug": slug,
                "title": title,
                "description": description,
                "image": image,
                "video_id": video_id,
                "duration": duration,
                "vi_sub": vi_sub,
                "en_sub": en_sub,
                "vi_transcript": vi_transcript,
                "en_transcript": en_transcript,
                "source": source_id if source_id else None,
                "sponsor": sponsor_id if sponsor_id else None,
            })

            if not video_form.is_valid():
                raise Exception(video_form.errors.as_json())
            
            video = video_form.save(commit=False)
            video.created_by = user
            video.created_at = timezone.now()
            video.save()

            for speaker_id in speaker_ids:
                video_speaker_form = forms.VideoSpeakerForm({
                    "video": video.id,
                    "speaker": speaker_id
                })
                if not video_speaker_form.is_valid():
                    raise Exception(video_speaker_form.errors.as_json())
                video_speaker_form.save()

            for category_id in category_ids:
                video_category_form = forms.VideoCategoryForm({
                    "video": video.id,
                    "category": category_id
                })
                if not video_category_form.is_valid():
                    raise Exception(video_category_form.errors.as_json())
                video_category_form.save()

            for subcategory_id in subcategory_ids:
                video_subcategory_form = forms.VideoSubCategoryForm({
                    "video": video.id,
                    "subcategory": subcategory_id
                })
                if not video_subcategory_form.is_valid():
                    raise Exception(video_subcategory_form.errors.as_json())
                video_subcategory_form.save()

            for tag in tags:
                tag_form = forms.TagForm({
                    "video": video.id,
                    "slug": name_to_slug(tag)
                })
                if not tag_form.is_valid():
                    raise Exception(tag_form.errors.as_json())
                tag_form.save()

            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(video).pk,
                object_id=video.id,
                object_repr=video.title,
                action_flag=ADDITION)

            return CreateVideo(video=video)


class UpdateVideo(graphene.Mutation):
    class Arguments:
        id = graphene.String()
        slug = graphene.String()
        title = graphene.String()
        description = graphene.String()
        image = graphene.String()
        video_id = graphene.String()
        duration = graphene.Int()
        vi_sub = graphene.String()
        en_sub = graphene.String()
        vi_transcript = graphene.String(default_value="")
        en_transcript = graphene.String(default_value="")
        source_id = graphene.String(default_value="")
        sponsor_id = graphene.String(default_value="")
        speaker_ids = graphene.List(graphene.String, default_value=[])
        category_ids = graphene.List(graphene.String, default_value=[])
        subcategory_ids = graphene.List(graphene.String, default_value=[])
        tags = graphene.List(graphene.String, default_value=[])

    video = graphene.Field(query.Video, slug=graphene.String())

    def mutate(self, info, id, slug, title, description, image, video_id, duration, vi_sub, en_sub, 
        vi_transcript, en_transcript, source_id, sponsor_id, speaker_ids, category_ids, subcategory_ids, tags):
        user = info.context.user

        if not get_permission('update_video', user, {"video": models.Video.objects.get(pk=id)}):
            raise Exception("Permission denied.")

        with transaction.atomic():
            video_form = forms.VideoForm(
                {
                    "slug": slug,
                    "title": title,
                    "description": description,
                    "image": image,
                    "video_id": video_id,
                    "duration": duration,
                    "vi_sub": vi_sub,
                    "en_sub": en_sub,
                    "vi_transcript": vi_transcript,
                    "en_transcript": en_transcript,
                    "source": source_id if source_id else None,
                    "sponsor": sponsor_id if sponsor_id else None,
                },
                instance=models.Video.objects.get(pk=id)
            )

            if not video_form.is_valid():
                raise Exception(video_form.errors.as_json())
            
            video = video_form.save(commit=False)
            video.updated_by = user
            video.updated_at = timezone.now()
            video.save()

            models.VideoSpeaker.objects.filter(video=video).delete()
            for speaker_id in speaker_ids:
                video_speaker_form = forms.VideoSpeakerForm({
                    "video": video.id,
                    "speaker": speaker_id
                })
                if not video_speaker_form.is_valid():
                    raise Exception(video_speaker_form.errors.as_json())
                video_speaker_form.save()

            models.VideoCategory.objects.filter(video=video).delete()
            for category_id in category_ids:
                video_category_form = forms.VideoCategoryForm({
                    "video": video.id,
                    "category": category_id
                })
                if not video_category_form.is_valid():
                    raise Exception(video_category_form.errors.as_json())
                video_category_form.save()

            models.VideoSubCategory.objects.filter(video=video).delete()
            for subcategory_id in subcategory_ids:
                video_subcategory_form = forms.VideoSubCategoryForm({
                    "video": video.id,
                    "subcategory": subcategory_id
                })
                if not video_subcategory_form.is_valid():
                    raise Exception(video_subcategory_form.errors.as_json())
                video_subcategory_form.save()

            models.Tag.objects.filter(video=video).delete()
            for tag in tags:
                tag_form = forms.TagForm({
                    "video": video.id,
                    "slug": name_to_slug(tag)
                })
                if not tag_form.is_valid():
                    raise Exception(tag_form.errors.as_json())
                tag_form.save()

            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(video).pk,
                object_id=video.id,
                object_repr=video.title,
                action_flag=CHANGE)

            return UpdateVideo(video=video)


class CreateSource(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()

    source = graphene.Field(query.Source, slug=graphene.String())

    def mutate(self, info, slug, name, description, image):
        user = info.context.user

        if not get_permission('create_source', user):
            raise Exception("Permission denied.")

        source_form = forms.SourceForm({
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
        })

        if not source_form.is_valid():
            raise Exception(source_form.errors.as_json())
        
        source = source_form.save()

        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(source).pk,
            object_id=source.id,
            object_repr=source.name,
            action_flag=ADDITION)

        return CreateSource(source=source)


class UpdateSource(graphene.Mutation):
    class Arguments:
        id = graphene.String()
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()

    source = graphene.Field(query.Source, slug=graphene.String())

    def mutate(self, info, id, slug, name, description, image):
        user = info.context.user

        if not get_permission('update_source', user):
            raise Exception("Permission denied.")

        source_form = forms.SourceForm({
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
        }, instance=models.Source.objects.get(pk=id))

        if not source_form.is_valid():
            raise Exception(source_form.errors.as_json())
        
        source = source_form.save()

        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(source).pk,
            object_id=source.id,
            object_repr=source.name,
            action_flag=CHANGE)

        return UpdateSource(source=source)


class CreateSpeaker(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()

    speaker = graphene.Field(query.Speaker, slug=graphene.String())

    def mutate(self, info, slug, name, description, image):
        user = info.context.user

        if not get_permission('create_speaker', user):
            raise Exception("Permission denied.")
        
        speaker_form = forms.SpeakerForm({
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
        })

        if not speaker_form.is_valid():
            raise Exception(speaker_form.errors.as_json())
        
        speaker = speaker_form.save()

        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(speaker).pk,
            object_id=speaker.id,
            object_repr=speaker.name,
            action_flag=ADDITION)

        return CreateSpeaker(speaker=speaker)


class UpdateSpeaker(graphene.Mutation):
    class Arguments:
        id = graphene.String()
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()

    speaker = graphene.Field(query.Speaker, slug=graphene.String())

    def mutate(self, info, id, slug, name, description, image):
        user = info.context.user

        if not get_permission('update_source', user):
            raise Exception("Permission denied.")
        
        speaker_form = forms.SpeakerForm({
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
        }, instance=models.Speaker.objects.get(pk=id))

        if not speaker_form.is_valid():
            raise Exception(speaker_form.errors.as_json())
        
        speaker = speaker_form.save()

        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(speaker).pk,
            object_id=speaker.id,
            object_repr=speaker.name,
            action_flag=CHANGE)

        return UpdateSpeaker(speaker=speaker)


class CreateCategory(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()
        priority = graphene.Int(default_value=1)

    category = graphene.Field(query.CategoryBasic, slug=graphene.String())

    def mutate(self, info, slug, name, description, image, priority):
        user = info.context.user

        if not get_permission('create_category', user):
            raise Exception("Permission denied.")

        category_form = forms.CategoryForm({
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
            "priority": priority,
        })

        if not category_form.is_valid():
            raise Exception(category_form.errors.as_json())
        
        category = category_form.save()

        return CreateCategory(category=category)


class CreateSubCategory(graphene.Mutation):
    class Arguments:
        category_slug = graphene.String()
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String(default_value="")
        image = graphene.String()
        priority = graphene.Int(default_value=1)

    subcategory = graphene.Field(query.SubCategory, slug=graphene.String())

    def mutate(self, info, category_slug, slug, name, description, image, priority):
        user = info.context.user

        if not get_permission('create_subcategory', user):
            raise Exception("Permission denied.")

        subcategory_form = forms.SubCategoryForm({
            "category": models.Category.objects.get(slug=category_slug).id,
            "slug": slug,
            "name": name,
            "description": description,
            "image": image,
            "priority": priority,
        })

        if not subcategory_form.is_valid():
            raise Exception(subcategory_form.errors.as_json())
        
        subcategory = subcategory_form.save()

        return CreateSubCategory(subcategory=subcategory)


class IncreaseViews(graphene.Mutation):
    class Arguments:
        slug = graphene.String()

    video = graphene.Field(query.Video, slug=graphene.String())

    def mutate(self, info, slug):
        video = models.Video.objects.get(is_published=True, slug=slug)
        video.view_amount += 1
        video.save()

        return IncreaseViews(video=video)


class PublishVideo(graphene.Mutation):
    class Arguments:
        id = graphene.String()

    video = graphene.Field(query.Video, id=graphene.String())

    def mutate(self, info, id):
        user = info.context.user

        if not get_permission('publish_video', user):
            raise Exception("Permission denied.")

        video = models.Video.objects.get(pk=id)
        video.is_published = True
        video.published_by = user
        video.published_at = timezone.now()
        video.save()

        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(video).pk,
            object_id=video.id,
            object_repr=video.title,
            action_flag=CHANGE,
            change_message="""[{"changed": {"fields": ["is_published", "published_by", "published_at"]}}]""")

        return PublishVideo(video=video)


class ImportVideo(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        title = graphene.String()
        description = graphene.String()
        image = graphene.String()
        video_id = graphene.String()
        duration = graphene.Int()
        vi_sub = graphene.String()
        en_sub = graphene.String()
        vi_transcript = graphene.String(default_value="")
        en_transcript = graphene.String(default_value="")
        view_amount = graphene.Int()
        is_published = graphene.Boolean()
        created_at = graphene.String()
        created_by = graphene.String()
        published_at = graphene.String()
        published_by = graphene.String()
        source = graphene.String(default_value="")
        sponsor = graphene.String(default_value="")
        speakers = graphene.List(graphene.String, default_value=[])
        categories = graphene.List(graphene.String, default_value=[])
        subcategories = graphene.List(graphene.String, default_value=[])
        tags = graphene.List(graphene.String, default_value=[])

    video = graphene.Field(query.Video, slug=graphene.String())

    def mutate(self, info, slug, title, description, image, video_id, duration, 
        vi_sub, en_sub, vi_transcript, en_transcript, view_amount, is_published, 
        created_at, created_by, published_at, published_by,
        source, sponsor, speakers, categories, subcategories, tags):

        user = info.context.user

        if not get_permission('import', user):
            raise Exception("Permission denied.")

        with transaction.atomic():
            try:
                models.Video.objects.get(slug=slug).delete()
            except:
                pass

            try:
                creator = User.objects.get(username=created_by)
            except User.DoesNotExist:
                creator = User.objects.get(username="admin")

            video_form = forms.VideoImportForm({
                "slug": slug,
                "title": title,
                "description": description,
                "image": image,
                "video_id": video_id,
                "duration": duration,
                "vi_sub": vi_sub,
                "en_sub": en_sub,
                "vi_transcript": vi_transcript,
                "en_transcript": en_transcript,
                "view_amount": view_amount,
                "is_published": is_published,
                "created_at": datetime.strptime(created_at[:19]+"+"+created_at[-5:-3]+created_at[-2:], '%Y-%m-%dT%H:%M:%S%z'),
                "created_by": creator.id,
                "published_at": datetime.strptime(published_at[:19]+"+"+published_at[-5:-3]+published_at[-2:], '%Y-%m-%dT%H:%M:%S%z'),
                "published_by": User.objects.get(username=published_by).id,
                "source": models.Source.objects.get(slug=source).id,
                "sponsor": User.objects.get(username=sponsor).id if sponsor else None,
            })

            if not video_form.is_valid():
                raise Exception(video_form.errors.as_json())
            
            video = video_form.save()

            for speaker in speakers:
                video_speaker_form = forms.VideoSpeakerForm({
                    "video": video.id,
                    "speaker": models.Speaker.objects.get(slug=speaker).id,
                })
                if not video_speaker_form.is_valid():
                    raise Exception(video_speaker_form.errors.as_json())
                video_speaker_form.save()

            for category in categories:
                video_category_form = forms.VideoCategoryForm({
                    "video": video.id,
                    "category": models.Category.objects.get(slug=category).id,
                })
                if not video_category_form.is_valid():
                    raise Exception(video_category_form.errors.as_json())
                video_category_form.save()

            for subcategory in subcategories:
                video_subcategory_form = forms.VideoSubCategoryForm({
                    "video": video.id,
                    "subcategory": models.SubCategory.objects.get(slug=subcategory).id,
                })
                if not video_subcategory_form.is_valid():
                    raise Exception(video_subcategory_form.errors.as_json())
                video_subcategory_form.save()

            for tag in tags:
                tag_form = forms.TagForm({
                    "video": video.id,
                    "slug": tag,
                })
                if not tag_form.is_valid():
                    raise Exception(tag_form.errors.as_json())
                tag_form.save()

            return ImportVideo(video=video)


class ImportUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        name = graphene.String(default_value="")
        email = graphene.String(default_value="")
        role = graphene.String()
        quote = graphene.String(default_value="")
        bio = graphene.String(default_value="")
        avatar = graphene.String(default_value="")
        cover = graphene.String(default_value="")
        facebook = graphene.String(default_value="")
        website = graphene.String(default_value="")

    user = graphene.Field(query.User, slug=graphene.String())

    def mutate(self, info, username, name, email, role, quote, bio, avatar, cover, facebook, website):

        user = info.context.user

        if not get_permission('import', user):
            raise Exception("Permission denied.")

        with transaction.atomic():
            user_form = forms.UserForm({
                "username": username,
                "first_name": name,
                "email": email,
            })

            if not user_form.is_valid():
                raise Exception(user_form.errors.as_json())
            
            user = user_form.save()

            profile_form = forms.ProfileForm({
                "user": user.id,
                "role": role,
                "quote": quote,
                "bio": bio,
                "avatar": avatar,
                "cover": cover,
                "facebook": facebook,
                "website": website,
            })

            if not profile_form.is_valid():
                raise Exception(profile_form.errors.as_json())

            profile_form.save()

            return ImportUser(user=user)


class ImportPlaylist(graphene.Mutation):
    class Arguments:
        slug = graphene.String()
        name = graphene.String()
        description = graphene.String()
        image = graphene.String()
        videos = graphene.List(graphene.String, default_value=[])

    playlist = graphene.Field(query.Playlist, slug=graphene.String())

    def mutate(self, info, slug, name, description, image, videos):

        user = info.context.user

        if not get_permission('import', user):
            raise Exception("Permission denied.")

        with transaction.atomic():
            playlist_form = forms.PlaylistForm({
                "slug": slug,
                "name": name,
                "description": description,
                "image": image,
            })

            if not playlist_form.is_valid():
                raise Exception(playlist_form.errors.as_json())
            
            playlist = playlist_form.save()

            for idx, video in enumerate(videos):
                playlist_video_form = forms.PlaylistVideoForm({
                    "video": models.Video.objects.get(slug=video).id,
                    "playlist": playlist.id,
                    "priority": idx+1,
                })
                if not playlist_video_form.is_valid():
                    raise Exception(playlist_video_form.errors.as_json())
                playlist_video_form.save()
            
            return ImportPlaylist(playlist=playlist)

class Mutation(graphene.ObjectType):
    create_video = CreateVideo.Field()
    update_video = UpdateVideo.Field()

    create_source = CreateSource.Field()
    update_source = UpdateSource.Field()

    create_speaker = CreateSpeaker.Field()
    update_speaker = UpdateSpeaker.Field()

    create_category = CreateCategory.Field()
    create_sub_category = CreateSubCategory.Field()

    increase_views = IncreaseViews.Field()
    publish_video = PublishVideo.Field()

    import_video = ImportVideo.Field()
    import_user = ImportUser.Field()
    import_playlist = ImportPlaylist.Field()
