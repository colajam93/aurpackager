from urllib.request import urlopen
from contextlib import closing


def save_to_file(url, file_path):
    with closing(urlopen(url)) as request:
        with open(file_path, 'wb') as f:
            f.write(request.read())
