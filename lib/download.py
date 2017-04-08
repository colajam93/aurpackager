from contextlib import closing
from urllib.request import urlopen, OpenerDirector


def save_to_file(url: str, file_path: str, opener: OpenerDirector = None):
    def process(request_):
        with open(file_path, 'wb') as f:
            f.write(request_.read())

    if opener:
        with closing(opener.open(url)) as request:
            process(request)
    else:
        with closing(urlopen(url)) as request:
            process(request)
