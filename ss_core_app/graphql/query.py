import graphene
from graphene import relay, InputObjectType
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import OrderingFilter, FilterSet, CharFilter

from graphql_relay.node.node import to_global_id

from django.db.models import Count, Case, When, Prefetch, Value, CharField, F, Sum
from django.db.models.query import Q
from django.db.models.functions import Concat
from django.contrib.auth import models as auth_models

from .. import models


class SubCategory(DjangoObjectType):
    class Meta:
        model = models.SubCategory
        
        
class SpeakerBasic(DjangoObjectType):
    class Meta:
        model = models.Speaker


class TagBasic(DjangoObjectType):
    class Meta:
        model = models.Tag
        
        
class CategoryBasic(DjangoObjectType):
    class Meta:
        model = models.Category


class Menu(DjangoObjectType):
    class Meta:
        model = models.Menu


class VideoFilter(FilterSet):
    class Meta:
        model = models.Video
        fields = ('is_published', )

    created_by = CharFilter(field_name='created_by__username')
    sponsor = CharFilter(field_name='sponsor__username')
    source = CharFilter(field_name='source__slug')
    # search = CharFilter(field_name='slug', lookup_expr='contains')
    search = CharFilter(method="search_filter")

    order_by = OrderingFilter(
        fields=(
            ('?', '?'),
            ('published_at', 'published_at'),
            ('id', 'id'),
            ('title', 'title'),
            ('duration', 'duration'),
            ('view_amount', 'view_amount'),
            ('playlistvideo__priority', 'playlistvideo__priority'),
        )
    )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | \
            Q(description__icontains=value) | \
            Q(videospeaker__speaker__name__icontains=value)
        )


class Video(DjangoObjectType):
    id = graphene.ID(required=True)
    speakers = graphene.List(SpeakerBasic)
    tags = graphene.List(TagBasic)
    categories = graphene.List(CategoryBasic)
    subcategories = graphene.List(SubCategory)

    class Meta:
        model = models.Video
        interfaces = (relay.Node, )
    
    def resolve_speakers(self, info, **kwargs):
        return models.Speaker.objects.filter(videospeaker__video=self)
    
    def resolve_tags(self, info, **kwargs):
        return models.Tag.objects.filter(video=self)
    
    def resolve_categories(self, info, **kwargs):
        return models.Category.objects.filter(videocategory__video=self)
        
    def resolve_subcategories(self, info, **kwargs):
        return models.SubCategory.objects.filter(videosubcategory__video=self)
    
    
class Speaker(DjangoObjectType):
    id = graphene.ID(required=True)
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)

    class Meta:
        model = models.Speaker
        interfaces = (graphene.Node, )
        
    def resolve_video_set(self, info, **kwargs):
        return models.Video.objects.filter(videospeaker__speaker=self)


class Source(DjangoObjectType):
    id = graphene.ID(required=True)
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)

    class Meta:
        model = models.Source
        interfaces = (graphene.Node, )
        
        
class User(DjangoObjectType):
    id = graphene.ID(required=True)
    slug = graphene.String()
    name = graphene.String()
    description = graphene.String()
    quote = graphene.String()
    avatar = graphene.String()
    image = graphene.String()
    cover = graphene.String()
    website = graphene.String()
    facebook = graphene.String()
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)

    class Meta:
        model = auth_models.User
        only_fields = ('username', 'first_name', 'last_name', 'video_set')
        exclude_fields = ('password', )
        interfaces = (graphene.Node, )
        
    def resolve_slug(self, info, **kwargs):
        return self.username
        
    def resolve_name(self, info, **kwargs):
        if not hasattr(self, 'name'):
            return self.get_full_name()
        else:
            return self.name
        
    def resolve_description(self, info, **kwargs):
        return self.profile.bio

    def resolve_quote(self, info, **kwargs):
        return self.profile.quote

    def resolve_avatar(self, info, **kwargs):
        return self.profile.avatar

    def resolve_image(self, info, **kwargs):
        return self.profile.avatar

    def resolve_cover(self, info, **kwargs):
        return self.profile.cover

    def resolve_website(self, info, **kwargs):
        return self.profile.website

    def resolve_facebook(self, info, **kwargs):
        return self.profile.facebook
        
        
class Category(DjangoObjectType):
    id = graphene.ID(required=True)
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)
    subcategories = graphene.List(SubCategory, order_by=graphene.String(default_value="priority"))

    class Meta:
        model = models.Category
        interfaces = (graphene.Node, )
        
    def resolve_video_set(self, info, **kwargs):
        return models.Video.objects.filter(videocategory__category=self)
    
    def resolve_subcategories(self, info, order_by, **kwargs):
        return self.subcategory_set.all().order_by(order_by)



class Tag(DjangoObjectType):
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)
    
    class Meta:
        model = models.Tag
        interfaces = (graphene.Node, )
        
    def resolve_video_set(self, info, **kwargs):
        return models.Video.objects.filter(tag=self)
        
        
class Playlist(DjangoObjectType):
    video_amount = graphene.Int()
    video_set = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)

    class Meta:
        model = models.Playlist
        interfaces = (graphene.Node, )
        
    def resolve_video_set(self, info, **kwargs):
        return models.Video.objects.filter(playlistvideo__playlist=self)
    
    
class SearchList(graphene.ObjectType):
    videos = DjangoConnectionField(Video)
    speakers = DjangoConnectionField(Speaker)
    sources = DjangoConnectionField(Source)
    

class Query(graphene.ObjectType):
    video = graphene.Field(Video, id=graphene.String(default_value=""), slug=graphene.String(default_value=""))
    def resolve_video(self, info, id, slug, **kwargs):
        try:
            if id:
                return models.Video.objects.get(id=id)
            return models.Video.objects.get(slug=slug)
        except models.Video.DoesNotExist:
            return None
    
    
    videos = DjangoFilterConnectionField(Video, filterset_class=VideoFilter)
    
    
    menus = graphene.List(Menu)
    def resolve_menus(self, info, **kwargs):
        return models.Menu.objects.all().order_by('priority')
    
    
    speaker = graphene.Field(Speaker, id=graphene.String(default_value=""), slug=graphene.String(default_value=""))
    def resolve_speaker(self, info, id, slug, **kwargs):
        try:
            if id:
                return models.Speaker.objects.get(id=id)
            return models.Speaker.objects.get(slug=slug)
        except models.Speaker.DoesNotExist:
            return None
        
        
    source = graphene.Field(Source, id=graphene.String(default_value=""), slug=graphene.String(default_value=""))
    def resolve_source(self, info, id, slug, **kwargs):
        try:
            if id:
                return models.Source.objects.get(id=id)
            return models.Source.objects.get(slug=slug)
        except models.Source.DoesNotExist:
            return None
        
        
    sponsor = graphene.Field(User, slug=graphene.String())
    def resolve_sponsor(self, info, slug, **kwargs):
        try:
            return auth_models.User.objects.get(username=slug)
        except auth_models.User.DoesNotExist:
            return None
    
        
    creator = graphene.Field(User, slug=graphene.String())
    def resolve_creator(self, info, slug, **kwargs):
        try:
            return auth_models.User.objects.get(username=slug)
        except auth_models.User.DoesNotExist:
            return None
        
        
    category = graphene.Field(Category, slug=graphene.String())
    def resolve_category(self, info, slug, **kwargs):
        try:
            return models.Category.objects.get(slug=slug)
        except models.Category.DoesNotExist:
            return None
        
        
    tag = graphene.Field(Tag, slug=graphene.String())
    def resolve_tag(self, info, slug, **kwargs):
        try:
            return models.Tag.objects.get(slug=slug)
        except models.Tag.DoesNotExist:
            return None
        
        
    playlist = graphene.Field(Playlist, slug=graphene.String())
    def resolve_playlist(self, info, slug, **kwargs):
        try:
            return models.Playlist.objects.get(slug=slug)
        except models.Playlist.DoesNotExist:
            return None

    
    search_list = graphene.Field(SearchList, query=graphene.String())
    def resolve_search_list(self, info, query, **kwargs):
        videos = models.Video.objects\
            .filter(
                Q(title__icontains=query) |\
                Q(description__icontains=query),
                is_published=True
            ).order_by('-published_at')
        
        speakers = models.Speaker.objects\
            .annotate(video_amount=Count(Case(When(videospeaker__video__is_published=True, then=1))))\
            .filter(Q(name__icontains=query))
            
        sources = models.Source.objects\
            .annotate(video_amount=Count(Case(When(video__is_published=True, then=1))))\
            .filter(Q(name__icontains=query))
        
        return SearchList(videos=videos, speakers=speakers, sources=sources)
        
            
    sources = DjangoConnectionField(Source, order_by=graphene.String(default_value=""), search=graphene.String(default_value=""))
    def resolve_sources(self, info, order_by, search, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return models.Source.objects\
            .filter(
                Q(name__icontains=search) |\
                Q(description__icontains=search)\
            )\
            .annotate(video_amount=Count(Case(When(video__is_published=True, then=1))))\
            .order_by(*orders)
            #.filter(video_amount__gt=0)\
            
            
    sponsors = DjangoConnectionField(User, order_by=graphene.String(default_value=""))
    def resolve_sponsors(self, info, order_by, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return auth_models.User.objects\
            .filter(profile__role="SP")\
            .annotate(video_amount=Count(Case(When(video_sponsor_by__is_published=True, then=1))))\
            .order_by(*orders)
            # .filter(video_amount__gt=0)\
            
            
    creators = DjangoConnectionField(User, order_by=graphene.String(default_value=""))
    def resolve_creators(self, info, order_by, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return auth_models.User.objects\
            .filter(profile__role="PO")\
            .annotate(video_amount=Count(Case(When(video_created_by__is_published=True, then=1))))\
            .order_by(*orders)
            # .filter(video_amount__gt=0)\


    speakers = DjangoConnectionField(Speaker, order_by=graphene.String(default_value=""), search=graphene.String(default_value=""))
    def resolve_speakers(self, info, order_by, search, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return models.Speaker.objects\
            .filter(
                Q(name__icontains=search) |\
                Q(description__icontains=search)\
            )\
            .annotate(video_amount=Count(Case(When(videospeaker__video__is_published=True, then=1))))\
            .order_by(*orders)
            
            
    # categories = graphene.List(Category, order_by=graphene.String(default_value=""))
    categories = DjangoConnectionField(Category, order_by=graphene.String(default_value=""))
    def resolve_categories(self, info, order_by, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return models.Category.objects\
            .annotate(video_amount=Count(Case(When(videocategory__video__is_published=True, then=1))))\
            .order_by(*orders)
            # .filter(video_amount__gt=0)\


    tags = DjangoConnectionField(Tag, order_by=graphene.String(default_value=""))
    def resolve_tags(self, info, order_by, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return models.Tag.objects\
            .annotate(video_amount=Count(Case(When(video__is_published=True, then=1))))\
            .order_by(*orders)
            # .filter(video_amount__gt=0)\


    playlists = DjangoConnectionField(Playlist, order_by=graphene.String(default_value=""))
    def resolve_playlists(self, info, order_by, **kwargs):
        if order_by:
            orders = (order_by, '-video_amount')
        else:
            orders = ('-video_amount', )
        
        return models.Playlist.objects\
            .annotate(video_amount=Count(Case(When(playlistvideo__video__is_published=True, then=1))))\
            .order_by(*orders)
            # .filter(video_amount__gt=0)\
