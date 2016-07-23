# AUR Packager

AUR package build server using Django.

## Requirement

- Arch Linux
- VM or container (This app use `sudo` for package installing so you should use them)

## Install

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
Static files are located at `/home/packager/aurpackager/static`.

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
