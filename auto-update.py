#!/usr/bin/env python3

import time
import urllib.request


def main():
    url = 'http://localhost:10081/api/build_all/?only_update=true'
    interval = 1800  # 30 minutes

    while True:
        urllib.request.urlopen(url)
        time.sleep(interval)


if __name__ == '__main__':
    main()
