from lib.pacman.command import execute


def refresh_force():
    """pacman -Syy"""
    execute('sudo -S pacman -Syy', discard_output=True)


def system_upgrade():
    """pacman -Syu"""
    execute('sudo -S pacman -Syu --noconfirm', discard_output=True)


def install(package, asdeps=False):
    """pacman -S [--asdeps] package"""
    option = ['--noconfirm']
    if asdeps:
        option.append('--asdeps')
    command = 'sudo -S pacman -S {} {}'.format(' '.join(option), package)
    execute(command, discard_output=True)


def exists(package):
    """check 'pacman -Si package' return code"""
    result = execute('pacman -Si {}'.format(package))
    return not bool(result.returncode)
