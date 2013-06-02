from django.conf.urls.defaults import *
from django.contrib import databrowse
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('select_song.views',
                       (r'^$', 'index'),
                       (r'login_task', 'login_task'),
                       (r'epl', 'epl'),
                       (r'register_task', 'register_task'),
                       (r'logout_task', 'logout_task'),
                       (r'append_to_playlist', 'append_to_playlist'),
                       (r'playlist_updated', 'playlist_updated'),
                       (r'search_result', 'search_result'),
                       (r'receive_message', 'receive_message'),
                       (r'remove_song', 'remove_song'),
                       (r'upload_song', 'upload_song'),
                       (r'usf', 'upload_song_file'),
                       (r'gmc', 'get_my_choices'),
                       (r'^databrowse/(.*)', login_required(databrowse.site.root)),
                       (r'rsv', 'rsv'),
                       (r'rename_song', 'rename_song'),
                       (r'gnb', 'next_batch'),
                       (r'gpb', 'prev_batch'),
                       (r'^.+$', 'boom'),
)

