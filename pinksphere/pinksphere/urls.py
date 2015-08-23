from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pinksphere.views.home', name='home'),
    # url(r'^pinksphere/', include('pinksphere.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^django/admin/', include(admin.site.urls)),
    ### apps
    # frontend
    url(r'', include('frontend.urls')),
    # chat
    url(r'^chat/', include('chat.urls')),
)
# media
urlpatterns += patterns("",
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)