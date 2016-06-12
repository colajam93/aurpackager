# AUR Packager

## Description

This application provides AUR package building on your server through web interface.
You can share AUR packages in all your machines through http.

## Requirement

- Arch Linux

## Install

- Create virtual environment

This application require no password sudo to install dependencies.
So you should run in VM or container.

- Create build user

```
# useradd -m -s /bin/bash packager
# echo 'packager ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
```

- Install dependencies

```
# pacman -S --needed base-devel python python-pip python-virtualenv bower git
```

- Prepare files

```
$ git clone https://github.com/colajam93/aurpackager
$ cd aurpackager
$ virtualenv venv
$ source venv/bin/activate
$ ./install_dependencies.sh
$ ./manage.py migrate
$ ./manage.py collectstatic --no-input
```

- Run server

Run development server or deploy to WSGI environment.

```
$ uwsgi --ini /home/packager/aurpackager/aurpackager.ini
```

## Automatic update checking

Use `build_all` api.
See `auto-update.py`.

## Slack Notification

Enable Incoming Webhooks and edit `packager/settings.py` as follows.

```
SLACK_NOTIFICATION = True
SLACK_NOTIFICATION_URL = 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'  # REQUIRED FOR SLACK_NOTIFICATION
AUR_PACKAGER_BASE_URL = 'https://aurpackager.yourdomain'  # REQUIRED FOR SLACK_NOTIFICATION
```


## License

MIT
