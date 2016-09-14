from lib.pacman.command import execute


def install(path):
    """pacman -U path"""
    command = 'sudo -S pacman -U --noconfirm {}'.format(path)
    return execute(command)
