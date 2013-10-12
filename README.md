vlctvstation
============

## Desctiption

Lets imgaine you are tiny organisation in a small town or even village, and you want to stream your own TV channel using your cable network.

Then you searching for software which could help you with this, all you need is steam few tv shows, news and ads, and here you find out,
that software you need costs huge money, and nobody cares you have only 5 viewers, well, this is kind of resolution of your problem.

This app has the scheduler, which you can manage using web interface:

![Screenshot](http://sets88.com/static/media/uploads/images/vlctvstation/vlctvstation.png)


You can add any content you want, and set when it have to be played:

![Screenshot](http://sets88.com/static/media/uploads/images/vlctvstation/vlctvstation2.png)


## Instalation and first run

In Ubuntu you can just copy this in terminal:

    sudo apt-get -y install git python-flask python-apscheduler
    git clone https://github.com/Sets88/vlctvstation.git
    cd vlctvstation/vlctvstation
    python vlctvstation.py

## Configuration

Configuration file loads on start it firstly tryes to open config file from:

"~/.vlctvstation.cfg"

if any error happened it will open "default.cfg" from current directory

There we have a simple formated json, i don't think it could raise any questions about this, but lets look on it:

    {
        "fullscreen": false, 
        "dbfile": "/tmp/dbfile", 
        "users": {
            "admin": "admin"
        }, 
        "permissions": {
            "add_jobs": [
                "admin"
            ], 
            "delete_jobs": [
                "admin" 
            ], 
            "run_jobs": [
                "admin"
            ], 
            "run_custom_jobs": [
                "admin"
            ], 
            "edit_jobs": [
                "admin"
            ], 
            "get_token": [
                "admin"
            ]
        }, 
        "language": "en", 
        "secret": "asfaesgdfsrtyweaslryuiryd", 
        "host": "0.0.0.0", 
        "port": "5000"
    }


fullscreen - you probably want to set it to true

dbfile - location of database file where all tasks stored

users - its dictionary where: "login": "password", you can also put comma and add another user like this

    "admin": "megasicretpass",
    "user": "supersecretpass"

permissions - use comma to add user a privilege you want like this

    "add_jobs": [
        "admin", "user"
    ],


language - if you read it, explaining not needed then

secret - change it firstly! It uses to generate token and as a salt for user's pass

host - IP or domain to listen on

post - port to listen on

## API

There is a way to check what is goin on know using API.

To use an API you have to generate a token first

![Screenshot](http://sets88.com/static/media/uploads/images/vlctvstation/vlctvstation3.png)


Enter an IP of node you want to use to get information, and click "Get"

Then copy the token you've got and make a url

    http://{ IP of VlcTVStation }/api/{ Token you've got }/status/


Lets test it:

    $ curl http://192.168.1.1:5000/api/0d17ee207e645270325cf43da8f101d461fd9f35/status/
    {"state": 3, "jobname": "Reklama", "uri": "/home/alexandra/video/Video.avi", "jobid": "905283"}

Now we see that state - 3 (Playing), current job's name, uri of file or url form video field, and jobid (never use it, it could change)
You can use this information as you want, as for me, i used it to show/hide external banner over the video on some tasks.
