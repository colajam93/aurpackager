import subprocess


def execute(command, discard_output=False):
    if discard_output:
        subprocess.Popen(command, shell=True, close_fds=True, stdin=None, stdout=None, stderr=None)
    else:
        return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True)
