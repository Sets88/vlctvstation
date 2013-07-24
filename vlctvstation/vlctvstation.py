#! /usr/bin/python
from flask import Flask
from flask import request, redirect, abort
from flask import render_template
from apscheduler.scheduler import Scheduler, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.shelve_store import ShelveJobStore
from datetime import datetime, timedelta
import vlc
from functools import wraps
from auth import Auth
from settings import settings
from mdict import MDict
import logging
logging.basicConfig()

app = Flask(__name__)

sched = Scheduler()

app.secret_key = str(settings['secret'])

auth = Auth(settings['users'], settings['secret'])

vlc_instance = vlc.Instance("--video-title-show --video-title-timeout 1 --sub-source marq")
media_player = vlc_instance.media_player_new()
audio_player = vlc_instance.media_player_new()
media_player.set_fullscreen(settings['fullscreen'])

em_mediaplayer = media_player.event_manager()

current_job = None

def event_end_reached_listener(event):
    """Adds a job to scheduler on now() + 1 sec to change media"""
    global current_job
    if current_job: 
        if current_job.kwargs['if_end_reached_run']:
            new_job = get_job_by_name(current_job.kwargs['if_end_reached_run'])
            current_job = new_job
            sched.add_date_job(change_media_sources, datetime.now()+timedelta(seconds=1), kwargs=new_job.kwargs, name="temporary_system_job")
            #run_job_by_name(current_job.kwargs['if_end_reached_run'])

def change_media_sources(uri, repeat=0, audio=None, if_end_reached_run=None, marq_options=None):
    options = []
    if audio is not None:
        options.append("no-audio")
    if repeat > 0:
        options.append("input-repeat=%d" % repeat)

    # Marquee
    if marq_options and 'marq_text' in marq_options:
        media_player.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 1)
        media_player.video_set_marquee_string(vlc.VideoMarqueeOption.Text, marq_options['marq_text'])
        if 'marq_color' in marq_options:
            media_player.video_set_marquee_int(vlc.VideoMarqueeOption.Color, marq_options['marq_color'])
        if 'marq_position' in marq_options:
            media_player.video_set_marquee_int(vlc.VideoMarqueeOption.Position, marq_options['marq_position'])
        if 'marq_x' in marq_options:
            media_player.video_set_marquee_int(vlc.VideoMarqueeOption.marquee_X, marq_options['marq_x'])
        if 'marq_y' in marq_options:
            media_player.video_set_marquee_int(vlc.VideoMarqueeOption.marquee_Y, marq_options['marq_y'])
        if 'marq_size' in marq_options:
            media_player.video_set_marquee_int(vlc.VideoMarqueeOption.Size, marq_options['marq_size'])        
    else:
        media_player.video_set_marquee_int(vlc.VideoMarqueeOption.Enable, 0)

    media = vlc_instance.media_new(uri)
    for option in options:
        media.add_options(option)

    audio_player.stop()
    audio_player.set_media(None)
    media_player.set_media(media)

    media_player.play()

    if audio:
        audio_media = vlc_instance.media_new(audio, "no-video")
        audio_player.set_media(audio_media)
        audio_player.play()


def get_last_date_from_job(job):
    now = datetime.now()
    dtdelta = timedelta(days=-1)
    last_time = job.get_run_times(now - dtdelta)
    if len(last_time) == 0:
        return job.next_run_time()
    else:
        return last_time.pop()


def run_last_job(jobs):
    last_jobs = sorted(jobs, key=get_last_date_from_job)
    if len(last_jobs) > 0:
        last_job = last_jobs.pop()
        last_job.func(**last_job.kwargs)
        global current_job
        current_job = last_job


def job_executed_listener(event):
    if event.job.name == "temporary_system_job":
        return None
    global current_job
    current_job = event.job


def run_job_by_id(id):
    for job in sched.get_jobs():
        if job.id == str(id):
            job.func(**job.kwargs)
            global current_job
            current_job = job
            return True
    return False


def get_job_by_name(name):
    for job in sched.get_jobs():
        if job.name == unicode(name):
            return job


def sched_add_job(**kwargs):
    new_kwargs = {'hour': None, 'day_of_week': None, 'week': None, 'day': None, 'month': None, 'year': None, 'name': None}
    func_kwargs = {'audio': None, 'repeat': None, 'if_end_reached_run': None, 'uri': None}
    marq_options = {}

    new_kwargs = MDict({'second': str, 'minute': str, 'hour': str, 'day_of_week': str, 'week': str, 'day': str, 'month': str, 'year': str, 'name': str, 'jobstore': str, 'kwargs': dict})
    func_kwargs = MDict({'audio': str, 'repeat': int, 'if_end_reached_run': str, 'uri': str, 'marq_options': dict})
    marq_options = MDict({'marq_text': str, 'marq_color': int, 'marq_position': int, 'marq_x': int, 'marq_y': int, 'marq_size': int})
    
    new_kwargs.update(kwargs)
    func_kwargs.update(kwargs)
    marq_options.update(kwargs)

    func_kwargs['marq_options'] = dict(marq_options)
    new_kwargs['jobstore'] = 'shelve'
    new_kwargs['kwargs'] = dict(func_kwargs)

    # if nothing filled, set cron, to far, far future
    if new_kwargs.has_not_a_single_item(['hour', 'day_of_week', 'week', 'day', 'month','year']):
        new_kwargs['year'] = '3000'

    sched.add_cron_job(change_media_sources, **dict(new_kwargs))


def get_job_info(job):
    info = {}
    info['id'] = job.id
    info['name'] = job.name
    info['kwargs'] = job.kwargs
    info['trigger'] = {}
    for field in job.trigger.fields:
        if field.is_default:
            info['trigger'][field.name] = ""
        else:
            info['trigger'][field.name] = str(field)
    return info

def get_player_info(player):
    res = {}
    media = player.get_media()
    res['state'] = media_player.get_state()
    if media:
        res['mrl'] = media.get_mrl()
    return res


# DECORATORS #############


def login_required(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        if auth.is_logged():
            return func(*args, **kwargs)
        else:
            return redirect("/login/")
    return wraper


def logged_in_or_404(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        if auth.is_logged():
            return func(*args, **kwargs)
        else:
            return abort(404)
    return wraper

# MAIN #################


@app.route("/login/", methods=["GET", "POST"])
def login():
    return auth.do_login_window()


@app.route("/logout/")
@logged_in_or_404
def logout():
    return auth.do_logout()


@app.route("/")
@login_required
def root():
    media = get_player_info(media_player)
    return render_template("jobs.html", jobs=sorted(sched.get_jobs()), media=media, datetime=datetime.now(), current_job=current_job)


@app.route("/addjob/", methods=["GET", "POST"])
@login_required
def add_job():
    if request.method == "POST":
        sched_add_job(**request.form.to_dict())
        return redirect("/")
    else:
        return render_template("addjob.html", jobs=sched.get_jobs())


@app.route("/deletejob/<int:id>/")
@login_required
def delete_job(id):
    for job in sched.get_jobs():
        if job.id == str(id):
            sched.unschedule_job(job)
            return redirect("/")
    abort(404)


@app.route("/runjob/<int:id>/")
@login_required
def run_job(id):
    if run_job_by_id(id):
        return redirect("/")
    else:
        abort(404)


@app.route("/editjob/<int:id>/", methods=["GET", "POST"])
@login_required
def edit_job(id):
    curr_job = None
    for job in sched.get_jobs():
        if job.id == str(id):
            curr_job = job
            break
    if curr_job is None:
        abort(404)
    if request.method == "POST":
        #try:
            sched_add_job(**request.form.to_dict())
        #except:
            #pass
        #else:
            sched.unschedule_job(curr_job)
            return redirect("/")
    return render_template("editjob.html", jobs=sched.get_jobs(), job=get_job_info(curr_job))


@app.route("/play/")
@login_required
def player_play():
    if media_player.get_media():
        if media_player.get_state() != 4:
            media_player.set_media(media_player.get_media())
        media_player.play()
    if audio_player.get_media():
        audio_player.play()
    return redirect("/")


@app.route("/pause/")
@login_required
def player_pause():
    if media_player.get_media():
        media_player.pause()
    if audio_player.get_media():
        audio_player.pause()
    return redirect("/")


@app.route("/open/", methods=["GET", "POST"])
@login_required
def player_open():
    if request.method == "POST":
        kwargs = {}
        if request.form['uri']:
            kwargs['uri'] = request.form['uri']
        if request.form['audio']:
            kwargs['audio'] = request.form['audio']
        if request.form['repeat']:
            kwargs['repeat'] = int(request.form['repeat'])

        global current_job
        current_job = None
        change_media_sources(**kwargs)

        return redirect("/")
    else:
        return render_template("open.html")


def main():
    sched.start()
    sched.add_jobstore(ShelveJobStore(settings['dbfile']), 'shelve')
    sched.add_listener(job_executed_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    run_last_job(sched.get_jobs())

    em_mediaplayer.event_attach(vlc.EventType.MediaPlayerEndReached, event_end_reached_listener)

    app.run(host=settings['host'], port=settings['port'])

if __name__ == "__main__":
    main()