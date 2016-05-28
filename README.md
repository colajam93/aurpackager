# AUR Packager

## Description

Auto AUR package builder with web interface using Django.

## Install

- Create virtual environment

This application require no password sudo to install depending packages.
So you should run in VM or container.

- Create build user

Execute following command as `root`.

```
# useradd -m -s /bin/bash packager
# echo 'packager ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
```

- Install depends

```
# pacman -S --needed base-devel python python-pip python-virtualenv bower git
```

- Prepare files

Execute following command as `packager`.

```
$ git clone URL
$ cd repository
$ virtualenv venv
$ source venv/bin/activate
$ ./install_dependencies.sh
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

- Run server

Run development server or deploy to WSGI environment.

```
$ ./manage.py runserver
```

## Add Package

1. Click 'Register' button.
2. Search with package name and select one from list.
3. Check detail and click 'Register' button.
If 'with dependencies' is enabled, dependency packages will be installed(official packages) and registered(AUR packages).

## TODO

- Authentication
- Error handling
- Auto update check
- Notification
- Remove package without admin page.
- Refactor
- Apply Bootstrap' grid system

## License

MIT
