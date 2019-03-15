from django.conf.urls import url, include
from django.contrib import admin
from ss_core.settings import DEBUG

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'', include('ss_core_app.urls')),
]

if DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)), 
        ] + urlpatterns
    except ImportError:
        pass
