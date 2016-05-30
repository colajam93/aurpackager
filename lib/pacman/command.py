import subprocess


def execute(command, discard_output=False):
    if discard_output:
        p = subprocess.run(command, shell=True, stdin=None, stdout=None, stderr=None)
        p.wait()
    else:
        return subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True)
