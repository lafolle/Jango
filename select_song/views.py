from django.http import HttpResponse, HttpResponseRedirect
from select_song.models import EnglishSong,Playlist, UserMessage,PrivilegeUser,UserChoice
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django import forms
import re
import os
import shutil

def clean_str(s):
    fc=''
    for c in s:
        if c== '<':
            fc+='&lt;'
        elif c=='>':
            fc+='&gt;'
        elif c=='\'':
            fc+='&amp;'
        elif c=='\"':
            fc+='&quot;'
        else:
            fc+=c
    return fc

def get_current_song():
    f= open('/home/kc/jango/status_data/current_song', 'r')
    c=f.readline()
    f.close()
    return c

def get_server_token():
    f = open('/home/kc/jango/status_data/server_pl_token', 'r')
    t = int(f.readline())
    f.close()
    return t
    
def set_server_token(token):
    f = open('/home/kc/jango/status_data/server_pl_token', 'w')
    f.write(str(token))
    f.close()

def update_server_token():
    k=get_server_token()
    set_server_token(k+1)
    
def index(request):
    return render_to_response('select_song/login.html',{},context_instance=RequestContext(request))

# Shorter version
@login_required
def epl(request):
    english_list = EnglishSong.objects.all().order_by('-times_played')[:30]
    return render_to_response('select_song/pl.html',
                              {'songs_list' : english_list, 'username' : request.user},)

def boom(request):
    return index(request)

def register_task(request):
    username = request.POST['username']
    passwd = request.POST['passwd']
    email = request.POST['email']
    if email=='' or passwd=='' or username=='':
        return HttpResponse('You did not give correct credentials.')
    try:
        user = User.objects.create_user(username, email, passwd)
    except IntegrityError:
        message = 'Username ' + username + ' already taken.'
        return render_to_response('select_song/login.html',
                                  {'error_message' : message},
                                  context_instance = RequestContext(request))
    user = authenticate(username=username, password=passwd)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('select_song.views.epl', args=()))
    return render_to_response('select_song/login.html',
                              {'error_message' : 'You are not autharized to access this app.'},
                              context_instance = RequestContext(request))

def login_task(request):
    username = request.POST['username']
    passwd = request.POST['passwd']
    user = authenticate(username=username, password=passwd)
    if user is not None and user.is_active and user.is_authenticated():
        login(request, user)
        return HttpResponseRedirect(reverse('select_song.views.epl', args=()))
    else:
        return render_to_response('select_song/login.html',
                              {'error_message' : 'You are not autharized to access this app.'},
                              context_instance = RequestContext(request))
                            
def logout_task(request):
    Playlist.objects.filter(user_name=request.user).delete()
    update_server_token()
    logout(request)
    return HttpResponseRedirect(reverse('select_song.views.index', args=()))

def update_choice_db(u, s):
    e = EnglishSong.objects.get(sname=s)
    try:
        u = UserChoice.objects.get(uname=u, song_record=e)
    except UserChoice.DoesNotExist:
        UserChoice(song_record=e, uname=u).save()

# look out for duplicate entries
@login_required
def append_to_playlist(request):
    if 'song_name' in request.GET and request.user.is_authenticated():
        sname = request.GET['song_name']
        update_choice_db(request.user, sname)
        try:
            p=EnglishSong.objects.get(sname=sname)
            p.times_played+=1
            p.save()
        except EnglishSong.MultipleObjectsReturned:
            p = EnglishSong.objects.filter(sname=sname)[:1]
        try:
            sin = Playlist.objects.get(song_record=p)
        except Playlist.DoesNotExist:
            update_server_token()
            Playlist(user_name=request.user, song_record=p).save()
            return HttpResponse('added')
        return HttpResponse('Redundant')
    return HttpResponse('Error in append_to_playlist')

def logintime(x):
    u=User(username=x)
    return u.last_login

def sort_by_logintime():
    d=[]
    for k in Playlist.objects.all():
        if k.user_name not in d and k.user_name is not 'AnonymousUser':
            d.append(k.user_name)
    sorted(d, key=logintime)
    return d

# No setting of server token
@login_required
def playlist_updated(request):
    cmc = request.GET['cmc']
    [mc,mcode]=get_messages(cmc)
    mcode=clean_str(mcode)
    if 'client_pl_token' in request.GET and request.user.is_authenticated():
        client_pl_token = int(request.GET['client_pl_token'])
        server_pl_token = get_server_token()
        if server_pl_token>client_pl_token:
            if len(Playlist.objects.all()) == 0:
                return HttpResponse('<?xml version="1.0" encoding="ISO-8859-1"?><response><code>empty</code><token>'+str(server_pl_token)+'</token><messages>'+mcode+'</messages><current_user></current_user><mtoken>'+str(mc)+'</mtoken></response>')
            pl = Playlist.objects.all()
            ul=[]
            ul = sort_by_logintime()
            cs=get_current_song()
            current_user = get_current_user()
            d={}
            for u in ul:
                d[u]=[]
            for elem in pl:
                d[elem.user_name].append(elem.song_record.sname)
            for k in d.keys():
                d[k] = sorted(d[k],key=byid)
            code='<response><code>'
            pcode ='<dl>'
            for k in d.keys():
                pcode += '<dt>'+k+'</dt>'
                for l in d[k]:
                    pcode+='<dd>'+l+'</dd>'
            pcode += '</dl>'
            fc=clean_str(pcode)
            code+=fc+'</code>'
            code+='<token>'+str(server_pl_token)+'</token>'+'<cs>'+clean_str(cs)+'</cs><current_user>'+current_user+'</current_user><messages>'+mcode+'</messages><mtoken>'+str(mc)+'</mtoken></response>'
            return HttpResponse(code)
        else:
            current_user = get_current_user()
            return HttpResponse('<?xml version="1.0" encoding="ISO-8859-1"?><response><code></code><token>'+str(server_pl_token)+'</token><current_user>'+current_user+'</current_user><messages>'+mcode+'</messages><mtoken>'+str(mc)+'</mtoken></response>')
    return HttpResponse('Token not found') 

def get_messages(cmc):
    code=''
    mc=UserMessage.objects.count()
    if cmc==mc:
        return [mc, code]
    l=UserMessage.objects.all().order_by('id')[cmc:]
    for m in l:
        code+='<p><span style="color : red">'+m.username+'</span> : '+str(m)+'</p>'
    return [ mc, code]
    
def get_current_user():
    f = open('/home/kc/jango/status_data/current_user', 'r')
    current_user = f.readline()
    f.close()
    return current_user

def byid(x):
    m=Playlist.objects.get(song_record=EnglishSong.objects.get(sname=x))
    return m.id

@login_required
def search_result(request):
    if 'search_song' in request.GET:
        s=request.GET['search_song']
        res = EnglishSong.objects.filter(sname__icontains=s.lower())
        code=''
        for m in res:
            code+='<li>'+str(m)+'</li>'
        return HttpResponse(code)
    else:
        return HttpResponse('Fuck!!!')

def receive_message(request):
    mesg = request.GET['mesg']
    p=UserMessage(username=request.user, message=mesg)
    p.save()
    return HttpResponse('Message added!!!')

def remove_song(request):
    song = request.GET['song']
    e=EnglishSong.objects.get(sname=song)
    Playlist.objects.get(song_record=e).delete()
    update_server_token()
    return HttpResponse('Your song has __ '+song+'__ been removed!')
    
@login_required
def upload_song(request):
    u = PrivilegeUser.objects.filter(username=request.user)
    if u:
        form = UploadSongForm()
        return render_to_response('select_song/upload_song.html', { 'form' : form}, context_instance = RequestContext(request))
    else:
        return HttpResponse('You are not authorised to upload files.')
#usf
def upload_song_file(request):
    if request.method == 'POST':
        form = UploadSongForm(request.POST, request.FILES)
        if form.is_valid():
            r = handle_song_file(request.FILES['file'])
            if r==1:
                return HttpResponse('Err in file name. Follow the rules!')
            elif r == 2:
                return HttpResponse('Song already exists!')
            else:
                return HttpResponseRedirect(reverse('select_song.views.epl', args=()))
        else:
            return HttpResponse('Someting went wrong!')

def clean_name(s):
    pat = r'(.+)\.m..$'
    match = re.search(pat, s, re.I)
    if match:
        return match.group(1)
    else:
        return ''

def handle_song_file(song_file):
    name = song_file.name
    dname = clean_name(name)
    if len(dname) == 0:
        return 1
    dname = dname.lower().capitalize()
    if os.path.exists('/home/kc/database_Song/'+dname):
        return 2
    destination = open('/home/kc/database_songs/'+dname, 'w')
    for chunk in song_file.chunks():
        destination.write(chunk)
    destination.close()
    EnglishSong(sname=dname,times_played=0).save()
    return 3

class UploadSongForm(forms.Form):
    file = forms.FileField()


def get_my_choices(request):
    l = UserChoice.get_choices(request.user)
    if l:
        s=''
        for k in l:
            s+='<li>'+k+'</li>'
        return HttpResponse(s)
    else:
        return HttpResponse('NULL')

#rsv
def rsv(request):
    return render_to_response('select_song/renamesong.html', {})

def rename_song(request):
    o_name = request.GET['old_name']
    n_name = request.GET['new_name']
    if o_name == n_name:
        return HttpResponse('Both names are same!')
    EnglishSong.objects.filter(sname=o_name).update(sname=n_name)
    r=r'/home/kc/database_songs/'
    shutil.move(r+o_name, r+n_name)
    return HttpResponse('Thanks for helping!')

def get_batch(f, c):
    code=''
    tc = EnglishSong.objects.count()
    if f>tc:
        return HttpResponse('')
    if c>0: # going forward
        if tc-f<c:
            l = EnglishSong.objects.all()[f:]
        else:
            l = EnglishSong.objects.all()[f:f+c]
    else:  # going back
        c=abs(c)
        if f<c:
            l = EnglishSong.objects.all()[0:f]
        else:
            l = EnglishSong.objects.all()[f-c:f]
    for k in l:
        code+='<li>'+str(k)+'</li>'
    return code
    
@login_required
def next_batch(request):
    f = int(request.GET['batch'])
    return HttpResponse(get_batch(f, 30))

@login_required
def prev_batch(request):
    f = int(request.GET['batch'])
    return HttpResponse(get_batch(f, -30))
    
        
