from graphene_django.views import GraphQLView

from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

import rest_framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.settings import api_settings

from .graphql.schema import schema
from . import views, apis

class DRFAuthenticatedGraphQLView(GraphQLView):
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super(GraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = api_view(['GET', 'POST'])(view)
        return view

urlpatterns = [
    url(r'^graphql_token', DRFAuthenticatedGraphQLView.as_view(schema=schema)),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),

    # Static
    url(r'^gioi-thieu/$', views.faq, name='faq'),
    url(r'^cau-hoi-thuong-gap/$', views.faq, name='faq'),
    url(r'^gop-y/$', views.gop_y, name='gop_y'),
    url(r'^dich-thuat/$', views.dich_thuat, name='dich_thuat'),
    url(r'^give/$', views.give, name='give'),
    url(r'^join/$', views.join, name='join'),
    url(r'^ss/$', views.video_list, name='video_list'),

    # APIs
    url(r'^api/user/$', apis.get_user),
    url(r'^api/upload/$', apis.upload_file),
    url(r'^api/youtube_duration/$', apis.youtube_duration),
]
