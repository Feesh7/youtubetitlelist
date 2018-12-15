#!/usr/local/bin/python3
import gevent.monkey
gevent.monkey.patch_all()

import gevent
import gevent.pool
import pprint
import argparse
import requests
import re

#FILL THIS IN
API_KEY = ""
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos?{args}"
GET_TITLE_API = YOUTUBE_API_URL.format(
    args="part=snippet&id={{urlid}}&key={key}".format(key=API_KEY))

YOUTUBE_ID_REGEX = re.compile(
    r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})',
    re.IGNORECASE)


def get_urlids_from_file(file):
    urls = (line for line in file if str(line).lower().startswith('http'))
    urlsids = (next(YOUTUBE_ID_REGEX.finditer(url), None) for url in urls)
    return (urlid.group(1) for urlid in urlsids if urlid)


def get_title(urlid):
    resp = requests.get(GET_TITLE_API.format(urlid=urlid))
    try:
        vidtitle = resp.json()["items"][0]["snippet"]["title"]
    except Exception:
        vidtitle = "[COULD NOT RESOLVE TITLE]"

    print("DEBUG: {} -> {}".format(urlid, vidtitle))
    return vidtitle


def list_youtube_vids(file, worker_count=100):
    WORKER_POOL = gevent.pool.Pool(size=worker_count)
    urlids = get_urlids_from_file(file)
    urldict = dict(WORKER_POOL.imap_unordered(
        lambda urlid: (urlid, get_title(urlid=urlid)),
        urlids))
    pprint.pprint(urldict, width=120)


def get_args():
    parser = argparse.ArgumentParser(description='List youtube video titles')
    parser.add_argument('file', type=argparse.FileType('r'))
    parser.add_argument('--worker-count', type=int, default=100)
    return vars(parser.parse_args())


if __name__ == "__main__":
    kargs = get_args()
    list_youtube_vids(**kargs)
