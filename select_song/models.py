from django.db import models


class EnglishSong(models.Model):
    sname = models.CharField(max_length=230)
    times_played = models.IntegerField()

    def __unicode__(self):
        return self.sname

    # return a list if songs from f to f+c
    def get_batch(f, c):
        code=''
        tc = English.objects.count()
        if c>0:
            if tc-f<c:
                l = EnglishSong.objects.all()[f:]
            else:
                l = EnglishSong.objects.all()[f:f+c]
        else:
            c=abs(c)
            if f<c:
                l = EnglishSong.objects.all()[0:f]
            else:
                l = EnglishSong.objects.all()[f-c:f]
        for k in l:
            code+='<li>'+str(k)+'</li'
        return code
        

class Playlist(models.Model):
    song_record  = models.ForeignKey('EnglishSong')
    user_name = models.CharField(max_length=230)

    def __unicode__(self):
        return self.song_record.sname

class UserMessage(models.Model):
    message = models.CharField(max_length=230)
    username=models.CharField(max_length=230)

    def __unicode__(self):
        return self.message

class PrivilegeUser(models.Model):
    username = models.CharField(max_length=230)

    def __unicode__(self):
        return self.username

class CandleLightSong(models.Model):
    sname = models.CharField(max_length=230)
    def __unicode__(self):
        return self.sname

class Database(models.Model):
    db_name = models.CharField(max_length=230)
    active = models.BooleanField()
    
    def __unicode__(self):
        return self.db_name

class UserChoice(models.Model):
    song_record = models.ForeignKey('EnglishSong')
    uname = models.CharField(max_length=230)

    def __unicode__(self):
        return self.song_record.sname+' by '+self.uname
    
    def get_choices(self, username):
        l = UserChoice.objects.filter(uname=username)
        rl = []
        for k in l:
            rl.append(str(k))
        return rl
    
