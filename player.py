#!/usr/bin/env python

import os
import sys
sys.path.append('/home/bnb/')
os.environ['DJANGO_SETTINGS_MODULE']='jango.settings'

import jango
import select_song

import vlc
import re
import commands
import random
from select_song.models import EnglishSong, Playlist
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from_playlist = False


def update_current_song(s):
    f=open('status_data/current_song', 'w')
    f.write(s)
    f.close()

    
def update_server_token():
    f = open('status_data/server_pl_token', 'r')
    t = int(f.readline())
    t += 1
    f.close()
    f =  open('status_data/server_pl_token', 'w')
    f.write(str(t))
    f.close()
    
def update_current_user(user):
    f = open('status_data/current_user', 'w')
    f.write(user)
    f.close()

def logintime(x):
    return User.objects.get(username=x).last_login

def sort_by_logintime():
    d=[]
    for k in Playlist.objects.all():
        if k.user_name not in d and k.user_name != 'AnonymousUser':
            d.append(k.user_name)
    sorted(d, key=logintime)
    return d

def byid(x):
    e = EnglishSong.objects.get(sname=x)
    return Playlist.objects.get(song_record=e).id

def get_new_dict():
    d = {}
    s_user = sort_by_logintime()
    # create latest dictionary
    for u in s_user:
        d[u] = []
    for e in Playlist.objects.all():
        if e.user_name in d.keys():
            d[e.user_name].append(e.song_record.sname)
        else:
            d[e.user_name] = [e.song_record.sname]
    for u in s_user:
        d[u] = sorted(d[u], key=byid)
        
    return d

def new_get_song(pd, nd, p_user):
    print pd
    print nd
    if p_user in nd.keys():
        c=nd.keys().index(p_user)
        if c==len(nd)-1:
            p_user = nd.keys()[0]
        else:
            p_user = nd.keys()[c+1]
    else:
        c=-1
        for person in pd.keys():
            if person in nd.keys():
                c+=1
                continue
            break
        if c != -1 and c is not len(nd)-1:
            p_user = nd.keys()[c+1]
        else:
            p_user = nd.keys()[0]
    return [ p_user, nd[p_user][0] ]

    
def play_song(sng):
    update_current_song(sng)
    update_server_token()
    print '\n\nPlaying -> '+sng
    mp = vlc.MediaPlayer('file:///home/bnb/database_songs/'+sng)
    mp.play()
    commands.getstatusoutput('sleep 2')
    dur = mp.get_length()/1000.0
    (status, output) = commands.getstatusoutput('sleep '+str(int(dur)+1))
    mp.release()
    global from_playlist
    if from_playlist:
        try:
            print 'Removing '+sng+' from Playlist...'
            e = EnglishSong.objects.get(sname=sng)
            Playlist.objects.get(song_record=e).delete()
            update_server_token()
            from_playlist=False
        except Playlist.DoesNotExist:
            print sng + ' does not exist in playlist!'
    
def get_song_from_predefined_source(sp):
    print 'Playing songs from predefined source..'
    update_current_user('None')
    ran = random.Random()
    return str(sp[ran.randint(1,EnglishSong.objects.count())])


p_played = []
def init():
    global from_playlist
    global p_played
    for j in range(0,3):
        p_played.append('')
    songs = EnglishSong.objects.all()
    sp=[]
    for e in songs:
        sp.append(str(e))

    new_batch=False
    pd=get_new_dict()
    nd=pd
    if len(nd) != 0:
        [ p_user, p_song] = play_new_batch(nd)
        prev_played(p_song)
    while True:
        nd=get_new_dict()

        if len(nd)==0:
            song=get_song_from_predefined_source(sp)
            from_playlist=False
            play_song(song)
            pd=get_new_dict()
            new_batch=True
            continue
        if new_batch:
            [p_user, p_song] = play_new_batch(nd)
            if prev_played(p_song):
                continue
            new_batch=False
        if len(get_new_dict())==0:
            continue
        [p_user, p_song] = new_get_song(pd, nd, p_user)
        if prev_played(p_song):
            continue
        from_playlist=True
        update_current_user(p_user)
        play_song(p_song)
        pd=nd

def play_new_batch(nd):
    global from_playlist
    user = nd.keys()[0]
    update_current_user(user)
    song = nd[user][0]
    from_playlist=True
    play_song(song)
    return [user, song]
        
def prev_played(song):
    global p_played
    if song in p_played:
        print 'Removing '+song+' song from Playlist'
        e=EnglishSong.objects.get(sname=song)
        try:
            Playlist.objects.get(song_record=e).delete()
        except Playlist.DoesNotExist:
            return True
        return True
    p_played.remove(p_played[0])
    p_played.append(song)
    print 'Previously played song are -> '+str(p_played)
    return False
    
if __name__=='__main__':
    init()
    

        
