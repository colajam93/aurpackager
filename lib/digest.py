import subprocess


def sha256(file):
    completed = subprocess.run(['sha256sum', file], stdout=subprocess.PIPE, universal_newlines=True)
    return completed.stdout.strip().split()[0]
