from django.conf.urls.defaults import *
from select_song.models import EnglishSong
from django.contrib import databrowse

from django.contrib import admin
admin.autodiscover()

databrowse.site.register(EnglishSong)

urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^static_media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root':'/home/kc/jango/static_media/', 'show_indexes':False}),
                       (r'', include('select_song.urls')),
)

