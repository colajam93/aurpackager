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
```

- Run server

Run development server or deploy to WSGI environment.

```
$ ./manage.py runserver
```

## TODO

- Auto update check
- Notification
- Refactor(Builder with coroutine?)
- File hash value
- Package filter

## License

MIT
