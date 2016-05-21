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
# pacman -S python python-pip python-virtualenv bower git
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

1. Access to admin page.
2. Add package.
Note: The name field must correspond to AUR package name.

## TODO

- Authentication
- Error handling
- Add package without admin page.
- Auto detect depend to AUR package.
- Auto update check
- Notification

## License

MIT
