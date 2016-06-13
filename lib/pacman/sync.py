from lib.pacman.command import execute


def refresh_force():
    """pacman -Syy"""
    execute('sudo -S pacman -Syy', discard_output=True)


def system_upgrade():
    """pacman -Syu"""
    execute('sudo -S pacman -Syu --noconfirm', discard_output=True)


def install(package, asdeps=False):
    """pacman -S [--asdeps] package"""
    option = ['--noconfirm', '--needed']
    if asdeps:
        option.append('--asdeps')
    command = 'sudo -S pacman -S {} {}'.format(' '.join(option), ' '.join(package))
    execute(command, discard_output=True)


def exist(package):
    """check 'pacman -Si package' return code"""
    result = execute('pacman -Ss "^{}$"'.format(package))
    return not bool(result.returncode)
