from select_song.models import Playlist, EnglishSong,UserMessage,PrivilegeUser,Database
from django.contrib import admin


class PlaylistAdmin(admin.ModelAdmin):
    search_fields = ['song_name', 'user_name']
    
admin.site.register(Playlist, PlaylistAdmin)

class EnglishSongAdmin(admin.ModelAdmin):
    search_fields = ['sname']
    
admin.site.register(EnglishSong, EnglishSongAdmin)
admin.site.register(UserMessage)
admin.site.register(PrivilegeUser)
admin.site.register(Database)
